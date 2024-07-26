import random
from operator import attrgetter
from pathlib import Path
from unittest import mock

import pydash
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from statemachine.exceptions import TransitionNotAllowed

from core.board.monopoly_swiss import create as create_monopoly_board
from core.device.models import Device
from core.exceptions import MaxParticipationsError, NotPlayersTurnError, ParticipationBlockedError, RollDiceNotAllowedError
from core.game.models import Character, Game, GameStatus, Participation
from core.game.participation import ParticipationStates
from core.testutils import (
    create_anonymous_client,
    create_board_client,
    create_character,
    create_player_client,
)

User = get_user_model()


class GameTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.board = create_monopoly_board()

    def test_creates_game(self):
        device = Device.objects.create(user_agent="user_agent")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        self.assertEqual(0, Game.objects.count())
        response = player_client.post(
            reverse("game-list"),
            data={"board": self.board.pk},
            headers={"X-Device-Token": device.token},
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            [GameStatus.CREATED],
            list(Game.objects.values_list("status", flat=True)),
        )

    def test_joining_requires_a_character(self):
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        game = Game.objects.create(owner=player, board=self.board, device=Device.objects.create())
        response = player_client.post(reverse("game-join", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            {
                "type": "validation_error",
                "errors": [
                    {
                        "attr": "character",
                        "code": "required",
                        "detail": "Dieses Feld ist zwingend erforderlich.",
                    },
                ],
            },
            response.json(),
        )

    def test_player_can_join_a_game(self):
        character = create_character(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        game = Game.objects.create(
            owner=User.objects.create(username="peter"), board=self.board, device=Device.objects.create()
        )

        response = player_client.post(
            reverse("game-join", kwargs={"pk": game.pk}),
            data={"character": character.pk},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            [GameStatus.CREATED],
            list(Game.objects.values_list("status", flat=True)),
        )
        self.assertEqual(
            [(player.pk, game.pk)],
            list(Participation.objects.values_list("player_id", "game_id")),
        )

    def test_player_can_only_join_once(self):
        character = create_character(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        game = Game.objects.create(
            owner=User.objects.create(username="peter"), board=self.board, device=Device.objects.create()
        )
        game.join(player, character)

        response = player_client.post(
            reverse("game-join", kwargs={"pk": game.pk}),
            data={"character": character.pk},
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            {
                "type": "validation_error",
                "errors": [
                    {
                        "code": "player_already_participating",
                        "detail": "Player is already participating",
                        "attr": None,
                    },
                ],
            },
            response.json(),
        )

    def test_player_can_only_join_a_fresh_game(self):
        character = create_character(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        game = Game.objects.create(
            status=GameStatus.FINISHED,
            owner=User.objects.create(username="peter"),
            board=self.board,
            device=Device.objects.create(),
        )
        response = player_client.post(
            reverse("game-join", kwargs={"pk": game.pk}),
            data={"character": character.pk},
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            {
                "type": "validation_error",
                "errors": [
                    {
                        "code": "game_has_already_started",
                        "detail": "Game has already started",
                        "attr": None,
                    },
                ],
            },
            response.json(),
        )

    def test_a_character_can_only_participate_once_in_a_game(self):
        character = create_character(name="Goblin", identifier="goblin")
        hans = User.objects.create(username="hans")
        hans_client = create_player_client(hans)
        peter = User.objects.create(username="peter")
        peter_client = create_player_client(peter)
        game = Game.objects.create(
            owner=User.objects.create(username="urs"), board=self.board, device=Device.objects.create()
        )
        hans_client.post(
            reverse("game-join", kwargs={"pk": game.pk}),
            data={"character": character.pk},
        )
        response = peter_client.post(
            reverse("game-join", kwargs={"pk": game.pk}),
            data={"character": character.pk},
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            {
                "type": "validation_error",
                "errors": [
                    {
                        "code": "unique_character",
                        "detail": "The characters have to be unique per game",
                        "attr": None,
                    },
                ],
            },
            response.json(),
        )

    def test_creating_a_game_sets_the_creator_as_the_owner(self):
        device = Device.objects.create(user_agent="user_agent")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        self.assertEqual(0, Game.objects.count())
        response = player_client.post(
            reverse("game-list"),
            data={"board": self.board.pk},
            headers={"X-Device-Token": device.token},
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            [player.pk],
            list(Game.objects.values_list("owner_id", flat=True)),
        )

    def test_restricts_maximum_amount_of_participants_per_game(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        urs = User.objects.create(username="urs")

        game = Game.objects.create(owner=hans, max_participations=2, board=self.board, device=Device.objects.create())
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.join(peter, create_character(name="Pirate", identifier="pirate"))
        with self.assertRaises(MaxParticipationsError):
            game.join(urs, create_character(name="Male", identifier="male"))

    def test_correctly_determines_whose_turn_is_next(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        urs = User.objects.create(username="urs")
        bruno = User.objects.create(username="bruno")
        game = Game.objects.create(owner=hans, board=self.board, device=Device.objects.create())

        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.join(peter, create_character(name="Pirate", identifier="pirate"))
        game.join(urs, create_character(name="Male", identifier="male"))
        game.join(bruno, create_character(name="Robot", identifier="robot"))

        self.assertEqual(None, game.current_turn)
        self.assertEqual(hans, game.next_turn)

        game.give_turn_to(peter)
        self.assertEqual(peter, game.current_turn)
        self.assertEqual(urs, game.next_turn)

        game.give_turn_to(bruno)
        self.assertEqual(bruno, game.current_turn)
        self.assertEqual(hans, game.next_turn)
        self.assertEqual(hans, game.next_turn)

    def test_determines_current_turn(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        urs = User.objects.create(username="urs")
        bruno = User.objects.create(username="bruno")
        game = Game.objects.create(owner=hans, board=self.board, device=Device.objects.create())

        participations = [
            game.join(hans, create_character(name="Goblin", identifier="goblin")),
            game.join(peter, create_character(name="Pirate", identifier="pirate")),
            game.join(urs, create_character(name="Male", identifier="male")),
            game.join(bruno, create_character(name="Robot", identifier="robot")),
        ]

        self.assertEqual(
            [False, False, False, False],
            list(map(attrgetter("is_players_turn"), participations)),
        )

        game.give_turn_to(peter)
        self.assertEqual(
            [False, True, False, False],
            list(map(attrgetter("is_players_turn"), participations)),
        )

        game.give_turn_to(bruno)
        self.assertEqual(
            [False, False, False, True],
            list(map(attrgetter("is_players_turn"), participations)),
        )

    def test_configure_max_participations(self):
        device = Device.objects.create(user_agent="user_agent")
        hans = User.objects.create(username="hans")

        hans_client = create_player_client(hans)
        response = hans_client.post(
            reverse("game-list"),
            data={"board": self.board.pk, "max_participations": 2},
            headers={"X-Device-Token": device.token},
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            [2],
            list(Game.objects.values_list("max_participations", flat=True)),
        )

    def test_configure_board(self):
        device = Device.objects.create(user_agent="user_agent")
        hans = User.objects.create(username="hans")

        hans_client = create_player_client(hans)
        response = hans_client.post(
            reverse("game-list"),
            data={"board": self.board.pk, "max_participations": 2},
            headers={"X-Device-Token": device.token},
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            [self.board.pk],
            list(Game.objects.values_list("board_id", flat=True)),
        )

    def test_configure_initial_balance(self):
        device = Device.objects.create(user_agent="user_agent")
        hans = User.objects.create(username="hans")

        hans_client = create_player_client(hans)
        response = hans_client.post(
            reverse("game-list"),
            data={"board": self.board.pk, "initial_balance": 1500},
            headers={"X-Device-Token": device.token},
        )
        game = Game.objects.get(pk=response.json()["pk"])
        self.assertEqual(1500, game.initial_balance)
        participation = game.join(hans, create_character("Zombie", "zombie"))
        self.assertEqual(1500, participation.balance)

    def test_lists_participations_for_a_game_lobby(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        game = Game.objects.create(owner=hans, board=self.board, device=Device.objects.create())
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.join(peter, create_character(name="Male", identifier="male"))

        player_client = create_player_client(hans)
        response = player_client.get(reverse("game-lobby", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(["hans", "peter"], pydash.pluck(response.json(), "player.username"))

    def test_only_the_owner_can_start_the_game(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        game = Game.objects.create(owner=hans, board=self.board, device=Device.objects.create())

        client = create_player_client(peter)
        response = client.post(reverse("game-start", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_reject_game_start_until_all_participants_have_joined(self):
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=2, board=self.board, device=Device.objects.create())
        game.join(hans, create_character(name="Goblin", identifier="goblin"))

        client = create_player_client(hans)
        response = client.post(reverse("game-start", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            {
                "errors": [
                    {
                        "attr": None,
                        "code": "lobby_not_ready",
                        "detail": "Not all participants have joined yet.",
                    },
                ],
                "type": "validation_error",
            },
            response.json(),
        )

    def test_can_only_start_a_created_or_paused_game(self):
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=1, board=self.board, device=Device.objects.create())
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.status = GameStatus.FINISHED
        game.save(update_fields=["status"])

        client = create_player_client(hans)
        response = client.post(reverse("game-start", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            {
                "errors": [
                    {
                        "attr": None,
                        "code": "game_start",
                        "detail": "Game is in the wrong status to start.",
                    },
                ],
                "type": "validation_error",
            },
            response.json(),
        )

    def test_get_participation_for_game_and_logged_in_player(self):
        hans = User.objects.create(username="hans")
        client = create_player_client(hans)
        game = Game.objects.create(owner=hans, board=self.board, device=Device.objects.create())

        response = client.get(reverse("game-participation", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        participation = game.join(hans, create_character(name="Goblin", identifier="goblin"))
        response = client.get(reverse("game-participation", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(participation.pk, response.json()["pk"])

    def test_annotates_is_lobby_is_full(self):
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, board=self.board, device=Device.objects.create(), max_participations=1)
        self.assertFalse(Game.objects.get(id=game.id).is_lobby_full)
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        self.assertTrue(Game.objects.get(id=game.id).is_lobby_full)

    def test_retrieving_a_game_or_the_lobby_is_also_possible_with_the_correct_device_token(self):
        hans = User.objects.create()
        device = Device.objects.create()
        game = Game.objects.create(owner=hans, board=self.board, device=device)

        client = create_anonymous_client()
        response = client.get(reverse("game-detail", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        board_client = create_board_client(str(device.token))
        response = board_client.get(reverse("game-detail", kwargs={"pk": game.pk}))
        self.assertEqual(game.pk, response.json()["pk"], response.json())

        response = board_client.get(reverse("game-lobby", kwargs={"pk": game.pk}))
        self.assertEqual([], response.json())


class GameLogicTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.board = create_monopoly_board()

    def setUp(self):
        super().setUp()
        self.hans = User.objects.create(username="hans")
        self.bruno = User.objects.create(username="bruno")

    def test_when_game_starts_hands_over_turn_to_first_player(self):
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=2, device=Device.objects.create())
        game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        game.start()
        self.assertEqual(self.bruno, game.current_turn)

    def test_current_tile_is_the_boards_first_tile(self):
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=2, device=Device.objects.create())
        game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.join(self.hans, create_character(name="Goblin", identifier="goblin"))

        self.assertEqual(
            ["start", "start"],
            list(Participation.objects.values_list("current_tile__identifier", flat=True)),
        )

    def test_player_cannot_move_if_its_not_its_turn(self):
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=2, device=Device.objects.create())
        game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        participation = game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        game.start()

        with self.assertRaises(NotPlayersTurnError):
            participation.move(10)

    def test_players_moves_steps_on_the_board(self):
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=2, device=Device.objects.create())
        participation = game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        game.start()

        self.assertEqual(
            ["start", "start"],
            list(Participation.objects.values_list("current_tile__identifier", flat=True)),
        )
        participation.move(1)
        self.assertEqual(
            ["chur_kornplatz", "start"],
            list(Participation.objects.values_list("current_tile__identifier", flat=True)),
        )

    def test_players_move_steps_on_the_board_using_dice(self):
        random.seed(42)
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=2, device=Device.objects.create())
        participation = game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        game.start()

        self.assertEqual(
            ["start", "start"],
            list(Participation.objects.values_list("current_tile__identifier", flat=True)),
        )
        participation.move_random()
        self.assertEqual(
            ["chance3", "start"],
            list(Participation.objects.values_list("current_tile__identifier", flat=True)),
        )

    def test_player_is_not_allowed_to_move_other_participation(self):
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=2, device=Device.objects.create())
        participation = game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        game.start()
        self.assertEqual(
            ["start", "start"],
            list(Participation.objects.values_list("current_tile__identifier", flat=True)),
        )
        client = create_player_client(self.hans)
        response = client.post(reverse("participation-move", kwargs={"pk": participation.pk}))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_players_move_steps_over_api(self):
        random.seed(42)
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=2, device=Device.objects.create())
        participation = game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        game.start()
        self.assertEqual(
            ["start", "start"],
            list(Participation.objects.values_list("current_tile__identifier", flat=True)),
        )
        client = create_player_client(self.bruno)
        response = client.post(reverse("participation-move", kwargs={"pk": participation.pk}))
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(
            ["chance3", "start"],
            list(Participation.objects.values_list("current_tile__identifier", flat=True)),
        )

    def test_ends_a_turn_over_the_api(self):
        random.seed(42)
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=2, device=Device.objects.create())
        participation = game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        game.start()
        client = create_player_client(self.bruno)

        self.assertEqual(ParticipationStates.IDLE.value, participation.state)
        client.post(reverse("participation-move", kwargs={"pk": participation.pk}))
        participation.refresh_from_db()
        self.assertEqual(ParticipationStates.MOVED.value, participation.state)

        client.post(reverse("participation-end-turn", kwargs={"pk": participation.pk}))
        participation.refresh_from_db()
        self.assertEqual(ParticipationStates.IDLE.value, participation.state)

    def test_cannot_roll_dice_twice_in_a_row(self):
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=1, device=Device.objects.create())
        participation = game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.start()
        participation.move(1)
        with self.assertRaises(RollDiceNotAllowedError):
            participation.move(1)

    def test_player_cannot_move_if_blocked(self):
        game = Game.objects.create(owner=self.hans, board=self.board, max_participations=1, device=Device.objects.create())
        participation = game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        game.start()
        participation.block()
        with self.assertRaises(ParticipationBlockedError):
            participation.move(1)


@override_settings(VALIDATE_GLTF=True)
class CharacterTestCase(TestCase):
    def test_model_is_required(self):
        with self.assertRaises(ValidationError):
            Character.objects.create(name="male", identifier="identifier")

    def test_only_accespts_gltf_files_for_model(self):
        try:
            Character.objects.create(
                name="male",
                identifier="identifier",
                model=SimpleUploadedFile("model.json", b"{}", "application/json"),
            )
            self.fail("Only .gltf file extension should be valid.")
        except ValidationError as e:
            self.assertIn(
                "Dateiendung „json“ ist nicht erlaubt. Erlaubte Dateiendungen sind: „gltf“.",
                e.messages,
            )

    def test_model_includes_necessary_animations(self):
        with (Path(__file__).parent / "fixtures" / "Casual_Male.gltf").open("rb") as gltf:
            Character.objects.create(
                name="male",
                identifier="identifier",
                model=SimpleUploadedFile("model.gltf", gltf.read(), "application/json"),
            )

        with self.assertRaisesMessage(
            ValidationError,
            "{'model': ['Missing animations on gltf model. Necessary animations: Idle, Walk, Run']}",
        ):
            Character.objects.create(
                name="male",
                identifier="identifier",
                model=SimpleUploadedFile("model.gltf", b"{}", "application/json"),
            )


class MQTTNotificationsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.board = create_monopoly_board()

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_a_game_is_created(self, mqtt_publish):
        device = Device.objects.create(user_agent="user_agent")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        response = player_client.post(
            reverse("game-list"),
            data={"board": self.board.pk},
            headers={"X-Device-Token": device.token},
        )
        self.assertIn(
            mock.call(f"{device.token}/game/created", {"id": response.json()["pk"]}),
            mqtt_publish.mock_calls,
        )

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_a_game_has_started(self, mqtt_publish):
        device = Device.objects.create()
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=1, board=self.board, device=device)
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.start()

        self.assertIn(
            mock.call(f"game/{game.pk}/changed", {"id": game.pk}),
            mqtt_publish.mock_calls,
        )

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_a_player_has_joined(self, mqtt_publish):
        device = Device.objects.create()
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=1, board=self.board, device=device)
        participation = game.join(hans, create_character(name="Goblin", identifier="goblin"))

        self.assertIn(
            mock.call("participation/created", {"id": participation.pk}),
            mqtt_publish.mock_calls,
        )

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_a_player_has_moved(self, mqtt_publish):
        device = Device.objects.create()
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=1, board=self.board, device=device)
        participation = game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.start()
        participation.move(1)

        self.assertIn(
            mock.call(f"participation/{participation.pk}/changed", {"id": participation.pk}),
            mqtt_publish.mock_calls,
        )

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_a_character_has_moved(self, mqtt_publish):
        device = Device.objects.create()
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=1, board=self.board, device=device)
        participation = game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.start()
        participation.move(1)

        self.assertIn(
            mock.call(f"game/{game.pk}/moved", {"id": participation.pk, "tile": "chur_kornplatz"}),
            mqtt_publish.mock_calls,
        )


class ParticipationTestCase(TestCase):
    def setUp(self):
        super().setUp()
        device = Device.objects.create()
        self.player = User.objects.create(username="hans")
        self.game = Game.objects.create(
            device=device, owner=self.player, board=create_monopoly_board(), max_participations=2
        )

    def test_initial_state_is_idle(self):
        participation = self.game.join(self.player, create_character("Goblin", "goblin"))
        self.assertEqual(ParticipationStates.IDLE.value, participation.state)

    def test_transitions_to_moved(self):
        peter = User.objects.create(username="peter")
        self.game.join(self.player, create_character("Goblin", "goblin"))
        peter_participation = self.game.join(peter, create_character("Zombie", "zombie"))
        self.game.start()
        with self.assertRaises(TransitionNotAllowed):
            peter_participation.statemachine.move()
        self.game.hand_over_turn()
        peter_participation.statemachine.move()
        self.assertEqual(ParticipationStates.MOVED.value, peter_participation.state)

    def test_automatically_transitions_to_moved(self):
        peter = User.objects.create(username="peter")
        participation = self.game.join(self.player, create_character("Goblin", "goblin"))
        self.game.join(peter, create_character("Zombie", "zombie"))
        self.game.start()

        participation.move(1)
        self.assertEqual(ParticipationStates.MOVED.value, participation.state)

    def test_ending_a_turn_passes_over_turn_and_transitions_back_to_idle(self):
        peter = User.objects.create(username="peter")
        participation = self.game.join(self.player, create_character("Goblin", "goblin"))
        peter_participation = self.game.join(peter, create_character("Zombie", "zombie"))
        self.game.start()

        participation.move(1)
        self.assertEqual(ParticipationStates.MOVED.value, participation.state)

        participation.end_turn()
        self.assertEqual(ParticipationStates.IDLE.value, participation.state)
        self.assertFalse(participation.is_players_turn)
        self.assertTrue(peter_participation.is_players_turn)
