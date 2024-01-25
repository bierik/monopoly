import random
from operator import methodcaller
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
from core.exceptions import MaxParticipationsExceeded
from core.game.models import Character, Game, GameStatus, Participation
from core.statemachine import GameMachine
from core.testutils import create_player_client

User = get_user_model()

with open(Path(__file__).parent / "fixtures" / "Casual_Male.gltf", "rb") as gltf:
    DEFAULT_CHARACTER_MODEL = gltf.read()


def create_character(name, identifier):
    return Character.objects.create(
        name=name,
        identifier=identifier,
        model=SimpleUploadedFile("model.gltf", DEFAULT_CHARACTER_MODEL, "application/json"),
    )


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
        game = Game.objects.create(owner=player, board=self.board)
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
                    }
                ],
            },
            response.json(),
        )

    def test_player_can_join_a_game(self):
        character = create_character(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        game = Game.objects.create(owner=User.objects.create(username="peter"), board=self.board)

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
        game = Game.objects.create(owner=User.objects.create(username="peter"), board=self.board)
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
                    }
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
                    }
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
        game = Game.objects.create(owner=User.objects.create(username="urs"), board=self.board)
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
                    }
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

        game = Game.objects.create(owner=hans, max_participations=2, board=self.board)
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.join(peter, create_character(name="Pirate", identifier="pirate"))
        with self.assertRaises(MaxParticipationsExceeded):
            game.join(urs, create_character(name="Male", identifier="male"))

    def test_correctly_determines_whose_turn_is_next(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        urs = User.objects.create(username="urs")
        bruno = User.objects.create(username="bruno")
        game = Game.objects.create(owner=hans, board=self.board)

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
        game = Game.objects.create(owner=hans, board=self.board)

        participations = [
            game.join(hans, create_character(name="Goblin", identifier="goblin")),
            game.join(peter, create_character(name="Pirate", identifier="pirate")),
            game.join(urs, create_character(name="Male", identifier="male")),
            game.join(bruno, create_character(name="Robot", identifier="robot")),
        ]

        self.assertEqual(
            [False, False, False, False],
            list(map(methodcaller("is_players_turn"), participations)),
        )

        game.give_turn_to(peter)
        self.assertEqual(
            [False, True, False, False],
            list(map(methodcaller("is_players_turn"), participations)),
        )

        game.give_turn_to(bruno)
        self.assertEqual(
            [False, False, False, True],
            list(map(methodcaller("is_players_turn"), participations)),
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

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_a_game_has_created_using_the_device_content(self, mqtt_publish):
        device = Device.objects.create(user_agent="user_agent")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        response = player_client.post(
            reverse("game-list"),
            data={"board": self.board.pk},
            headers={"X-Device-Token": device.token},
        )
        mqtt_publish.assert_called_with(f"{device.token}/game/created", {"game_id": response.json()["pk"]})

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_a_game_receives_a_participation(self, mqtt_publish):
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, board=self.board)
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        mqtt_publish.assert_called_with(f"game/{game.pk}/joined", {"game_id": game.pk})

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_all_participants_have_joined_the_game(self, mqtt_publish):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        game = Game.objects.create(owner=hans, board=self.board, max_participations=2)
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.join(peter, create_character(name="Zombie", identifier="zombie"))
        mqtt_publish.assert_called_with(f"game/{game.pk}/all_joined", {"game_id": game.pk})

    def test_lists_participations_for_a_game_lobby(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        game = Game.objects.create(owner=hans, board=self.board)
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.join(peter, create_character(name="Male", identifier="male"))

        player_client = create_player_client(hans)
        response = player_client.get(reverse("game-lobby", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(["hans", "peter"], pydash.pluck(response.json(), "player.username"))

    def test_only_the_owner_can_start_the_game(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        game = Game.objects.create(owner=hans, board=self.board)

        client = create_player_client(peter)
        response = client.post(reverse("game-start", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_reject_game_start_until_all_participants_have_joined(self):
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=2, board=self.board)
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
                    }
                ],
                "type": "validation_error",
            },
            response.json(),
        )

    def test_can_only_start_a_created_or_paused_game(self):
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=1, board=self.board)
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
                    }
                ],
                "type": "validation_error",
            },
            response.json(),
        )

    @mock.patch("core.mqtt_client.mqtt_client.publish")
    def test_notifies_when_a_game_has_started(self, mqtt_publish):
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans, max_participations=1, board=self.board)
        game.join(hans, create_character(name="Goblin", identifier="goblin"))
        game.start()
        mqtt_publish.assert_called_with(f"game/{game.pk}/started", {"game_id": game.pk})

    def test_get_participation_for_game_and_logged_in_player(self):
        hans = User.objects.create(username="hans")
        client = create_player_client(hans)
        game = Game.objects.create(owner=hans, board=self.board)

        response = client.get(reverse("game-participation", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        participation = game.join(hans, create_character(name="Goblin", identifier="goblin"))
        response = client.get(reverse("game-participation", kwargs={"pk": game.pk}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(participation.pk, response.json()["pk"])


class GameMaschineTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.board = create_monopoly_board()

    def setUp(self):
        super().setUp()
        self.hans = User.objects.create(username="hans")
        self.game = Game.objects.create(owner=self.hans, board=self.board)
        self.urs = User.objects.create(username="urs")
        self.bruno = User.objects.create(username="bruno")

    def test_persists_state(self):
        participation = self.game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        self.assertEqual("idle", participation.state)

        self.game.hand_over_turn()
        participation.statemachine.start_turn()

    def test_restricts_turn_to_players_turn(self):
        hans_machine = self.game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        bruno_machine = self.game.join(self.bruno, create_character(name="Pirate", identifier="pirate"))
        urs_machine = self.game.join(self.urs, create_character(name="Male", identifier="male"))

        machines = [hans_machine, bruno_machine, urs_machine]

        self.assertEqual(["idle", "idle", "idle"], pydash.pluck(machines, "state"))

        with self.assertRaises(TransitionNotAllowed):
            hans_machine.statemachine.start_turn()

        self.game.hand_over_turn()

        hans_machine.statemachine.start_turn()
        self.assertEqual(["turn_started", "idle", "idle"], pydash.pluck(machines, "state"))

    def test_hands_over_turn_to_next_player(self):
        hans_machine = GameMachine(self.game.join(self.hans, create_character(name="Goblin", identifier="goblin")))
        self.game.join(self.bruno, create_character(name="Goblin", identifier="goblin"))
        self.game.hand_over_turn()
        hans_machine.start_turn()
        hans_machine.roll_dice()
        hans_machine.move()
        hans_machine.end_turn()

        self.game.refresh_from_db(fields=["current_turn"])
        self.assertEqual(self.bruno, self.game.current_turn)

    def test_moves_some_steps_on_the_board(self):
        random.seed(42)

        participation = self.game.join(self.hans, create_character(name="Goblin", identifier="goblin"))
        hans_machine = GameMachine(participation)
        self.game.hand_over_turn()
        hans_machine.start_turn()
        self.assertEqual(self.board.tiles.get(identifier="start"), participation.current_tile)
        hans_machine.roll_dice()
        self.assertEqual(self.board.tiles.get(identifier="chance3"), participation.current_tile)


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
        with open(Path(__file__).parent / "fixtures" / "Casual_Male.gltf", "rb") as gltf:
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
