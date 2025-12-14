from unittest import mock

from django.db import transaction
from rest_framework.test import APITestCase

from app.action.action import Action
from app.action.action import NoopAction
from app.action.built_in_actions import JailAction
from app.action.built_in_actions import PunishAction
from app.action.built_in_actions import StartAction
from app.action.exceptions import ActionNotFoundError
from app.action.exceptions import InvalidActionDeclarationError
from app.action.exceptions import InvalidActionNameError
from app.action.exceptions import InvalidActionTriggersError
from app.action.registry import action_registry
from app.action.registry import register
from app.action.trigger import Triggers
from app.board.models import Board
from app.board.models import Direction
from app.board.models import Tile
from app.board.models import TileTypes
from app.device.models import Device
from app.game.models import Game
from app.game.models import Participation
from tests.utils import create_character
from tests.utils import create_player


class ValidAction(Action):
    pass


class ActionTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        action_registry.clear()
        action_registry.register(NoopAction)
        action_registry.register(StartAction)
        action_registry.register(PunishAction)
        action_registry.register(JailAction)
        self.board = Board.objects.create(name="test")
        device = Device.objects.create()
        self.player = create_player()
        self.game = Game.objects.create(device=device, owner=self.player, board=self.board, max_participations=1)

    def create_participation(self, tile, **kwargs):
        return Participation.objects.create(
            game=self.game,
            player=self.player,
            character=create_character("Zombie", "zombie"),
            current_tile=tile,
            **kwargs,
        )

    def test_actions_must_have_necessary_attributes(self):
        class DoesNotSubclassAction:
            pass

        with self.assertRaises(InvalidActionDeclarationError):
            action_registry.register(DoesNotSubclassAction)

    def test_registers_actions_in_registry(self):
        action_registry.register(ValidAction)
        self.assertEqual(ValidAction, action_registry.store["ValidAction"])

    def test_retrieve_action_for_name(self):
        with self.assertRaises(ActionNotFoundError):
            action_registry.for_name("missing")

        action_registry.register(ValidAction)
        self.assertEqual(ValidAction, action_registry.for_name("ValidAction"))

    def test_registers_action_using_contextmanager(self):
        @register()
        class AutoValidAction(ValidAction):
            pass

        self.assertEqual(AutoValidAction, action_registry.for_name("AutoValidAction"))

    def test_call_action_for_name(self):
        @register()
        class CallableAction(ValidAction):
            run = mock.Mock()

        tile = Tile.objects.create(
            identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, action=CallableAction
        )
        participation = self.create_participation(tile)

        action_registry.call_for_name("CallableAction", participation=participation, trigger=None)
        CallableAction.run.assert_called_once()

    def test_asks_registry_if_action_exists(self):
        self.assertFalse(action_registry.exists("missing"))

        action_registry.register(ValidAction)
        self.assertTrue(action_registry.exists("ValidAction"))
        self.assertTrue(action_registry.exists(ValidAction))

    def test_only_allow_registering_action_to_a_tile_that_has_been_registered(self):
        class CallableAction(ValidAction):
            pass

        with transaction.atomic(), self.assertRaises(InvalidActionNameError):
            Tile.objects.create(identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, action=CallableAction)

        action_registry.register(CallableAction)
        tile = Tile.objects.create(
            identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, action=CallableAction
        )
        self.assertEqual(CallableAction, tile.action)

    def test_calling_action_on_a_tile_passes_context(self):
        @register()
        class CallableAction(ValidAction):
            run = mock.Mock()

        tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            action=CallableAction,
            board=self.board,
        )

        participation = self.create_participation(tile)
        tile.call_action(participation, None)
        CallableAction.run.assert_called_with(participation=participation, tile=tile, context={})

    def test_validates_action_triggers(self):
        class InvalidTriggerAction(ValidAction):
            triggers = ["invalid"]

        with self.assertRaises(InvalidActionTriggersError):
            action_registry.register(InvalidTriggerAction)

        class ValidTriggerAction(ValidAction):
            triggers = [Triggers.TRAVERSED]

        action_registry.register(ValidTriggerAction)

    def test_lands_on_trigger(self):
        @register()
        class LandsOnAction(ValidAction):
            triggers = [Triggers.LANDED_ON]
            run = mock.Mock()

        tile = Tile.objects.create(
            identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, board=self.board, order=0
        )
        lands_on_tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            action=LandsOnAction,
            board=self.board,
            order=1,
        )
        participation = self.create_participation(tile)
        self.game.start()
        participation.move(1)
        LandsOnAction.run.assert_called_with(participation=participation, tile=lands_on_tile, context={})

    def test_traversed_trigger(self):
        @register()
        class TraverseAction(ValidAction):
            triggers = [Triggers.TRAVERSED]
            run = mock.Mock()

        tile = Tile.objects.create(
            identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, board=self.board, order=0
        )
        Tile.objects.create(identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, board=self.board, order=1)
        lands_on_tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            action=TraverseAction,
            board=self.board,
            order=1,
        )
        participation = self.create_participation(tile)
        self.game.start()
        participation.move(5)
        self.assertEqual(
            [
                mock.call(participation=participation, tile=lands_on_tile, context={}),
                mock.call(participation=participation, tile=lands_on_tile, context={}),
            ],
            TraverseAction.run.mock_calls,
        )

    def test_start_action(self):
        tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            action=StartAction,
            board=self.board,
            order=1,
        )
        participation = self.create_participation(tile)
        action_registry.call_for_name("StartAction", participation=participation, trigger=Triggers.TRAVERSED)
        self.assertEqual(200, participation.balance)

    def test_passes_action_context_to_call(self):
        @register()
        class ActionWithContext(ValidAction):
            triggers = [Triggers.TRAVERSED]
            run = mock.Mock()

        tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            board=self.board,
            order=1,
            action=ActionWithContext,
            action_context={"value": 1},
        )
        participation = self.create_participation(tile)
        tile.call_action(participation, Triggers.TRAVERSED)
        self.assertEqual(
            [
                mock.call(participation=participation, tile=tile, context={"value": 1}),
            ],
            ActionWithContext.run.mock_calls,
        )

    def test_serializes_action(self):
        class ActionToSerialize(ValidAction):
            title = "Title"
            text = "Text"

        action = ActionToSerialize()
        self.assertEqual({"title": "Title", "text": "Text"}, action.serialize())

    def test_serializes_action_from_context(self):
        @register()
        class ActionToSerialize(ValidAction):
            title = "Title"
            text = "Text"

        action = ActionToSerialize()
        self.assertEqual({"title": "Title", "text": "Text"}, action.serialize())
        self.assertEqual(
            {"title": "Another title", "text": "Another text"},
            action.serialize({"text": "Another text", "title": "Another title"}),
        )

    def test_punish_action(self):
        tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            board=self.board,
            order=1,
            action=PunishAction,
        )
        participation = self.create_participation(tile, balance=1000)
        tile.call_action(participation, Triggers.LANDED_ON)
        self.assertEqual(800, participation.balance)

    def test_punish_action_with_custom_balance(self):
        tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            board=self.board,
            order=1,
            action=PunishAction,
            action_context={"punishment": 500},
        )
        participation = self.create_participation(tile, balance=1000)
        tile.call_action(participation, Triggers.LANDED_ON)
        self.assertEqual(500, participation.balance)

    def test_jail_action(self):
        tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            board=self.board,
            order=1,
            action=JailAction,
        )
        participation = self.create_participation(tile)
        tile.call_action(participation, Triggers.LANDED_ON)
        self.assertTrue(participation.is_blocked)

    @mock.patch("app.mqtt_client.mqtt_client.publish")
    def test_notifies_serialized_action(self, mqtt_publish):
        @register()
        class ActionToSerialize(ValidAction):
            title = "Title"
            text = "Text"
            triggers = [Triggers.LANDED_ON]

        tile = Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            board=self.board,
            order=1,
            action=ActionToSerialize,
        )
        participation = self.create_participation(tile)
        tile.call_action(participation, Triggers.LANDED_ON)

        self.assertIn(
            mock.call(
                f"participation/{participation.pk}/action",
                {"id": participation.pk, "action": {"title": "Title", "text": "Text"}},
            ),
            mqtt_publish.mock_calls,
        )

    def test_validates_action_context(self):
        Tile.objects.create(
            identifier="test",
            type=TileTypes.CORNER,
            direction=Direction.BOTTOM,
            board=self.board,
            order=1,
            action_context={"unknown": 1, "punishment": "not a number"},
        )
