from unittest import mock

from django.db import transaction
from rest_framework.test import APITestCase

from core.action.action import Action, NoopAction
from core.action.built_in_actions import StartAction
from core.action.exceptions import (
    ActionNotFoundError,
    InvalidActionDeclarationError,
    InvalidActionNameError,
    InvalidActionTriggersError,
)
from core.action.registry import action_registry, register
from core.action.trigger import Triggers
from core.board.models import Board, Direction, Tile, TileTypes
from core.board.monopoly_swiss import create as create_monopoly_board
from core.device.models import Device
from core.game.models import Game, Participation
from core.testutils import create_character, create_player


class ValidAction(Action):
    pass


class ActionTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        action_registry.clear()
        action_registry.register(NoopAction)
        action_registry.register(StartAction)

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

        action_registry.call_for_name("CallableAction", participation=None, trigger=None)
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
            identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, action=CallableAction
        )

        device = Device.objects.create()
        player = create_player()
        game = Game.objects.create(device=device, owner=player, board=create_monopoly_board())
        participation = Participation.objects.create(
            game=game, player=player, character=create_character("Zombie", "zombie"), current_tile=tile
        )
        tile.call_action(participation, None)
        CallableAction.run.assert_called_with(participation=participation)

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

        board = Board.objects.create(name="test")
        Tile.objects.create(identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, board=board, order=0)
        Tile.objects.create(
            identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, action=LandsOnAction, board=board, order=1
        )
        device = Device.objects.create()
        player = create_player()
        game = Game.objects.create(device=device, owner=player, board=board, max_participations=1)
        participation = game.join(player=player, character=create_character("Zombie", "zombie"))
        game.start()
        participation.move(1)
        LandsOnAction.run.assert_called_with(participation=participation)

    def test_traversed_trigger(self):
        @register()
        class TraverseAction(ValidAction):
            triggers = [Triggers.TRAVERSED]
            run = mock.Mock()

        board = Board.objects.create(name="test")
        Tile.objects.create(identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, board=board, order=0)
        Tile.objects.create(identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, board=board, order=1)
        Tile.objects.create(
            identifier="test", type=TileTypes.CORNER, direction=Direction.BOTTOM, action=TraverseAction, board=board, order=1
        )
        device = Device.objects.create()
        player = create_player()
        game = Game.objects.create(device=device, owner=player, board=board, max_participations=1)
        participation = game.join(player=player, character=create_character("Zombie", "zombie"))
        game.start()
        participation.move(5)
        self.assertEqual(
            [
                mock.call(participation=participation),
                mock.call(participation=participation),
            ],
            TraverseAction.run.mock_calls,
        )

    def test_start_action(self):
        board = create_monopoly_board()
        device = Device.objects.create()
        player = create_player()
        game = Game.objects.create(device=device, owner=player, board=board, max_participations=1)
        participation = game.join(player=player, character=create_character("Zombie", "zombie"), balance=1000)

        action_registry.call_for_name("StartAction", participation=participation, trigger=Triggers.TRAVERSED)
        self.assertEqual(1200, participation.balance)
