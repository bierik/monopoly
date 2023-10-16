from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.game.models import (
    Board,
    Character,
    Game,
    GameStatus,
    MaxParticipationsExceeded,
    Participation,
)
from core.testutils import create_player_client

User = get_user_model()


class GameTestCase(APITestCase):
    def test_creating_a_game_requires_character(self):
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        response = player_client.post(reverse("game-list"))
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

    def test_creates_game(self):
        character = Character.objects.create(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        self.assertEqual(0, Game.objects.count())
        response = player_client.post(
            reverse("game-list"), data={"character": character.pk}
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            [GameStatus.CREATED],
            list(Game.objects.values_list("status", flat=True)),
        )

    def test_joining_requires_a_character(self):
        game = Game.objects.create(owner=User.objects.create(username="hans"))
        response = self.client.post(reverse("game-join", kwargs={"pk": game.pk}))
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
        character = Character.objects.create(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        game = Game.objects.create(owner=User.objects.create(username="peter"))

        response = player_client.post(
            reverse("game-join", kwargs={"pk": game.pk}),
            data={"character": character.pk},
        )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(
            [GameStatus.CREATED],
            list(Game.objects.values_list("status", flat=True)),
        )
        self.assertEqual(
            [(player.pk, game.pk)],
            list(Participation.objects.values_list("player_id", "game_id")),
        )

    def test_player_can_only_join_once(self):
        character = Character.objects.create(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        game = Game.objects.create(owner=User.objects.create(username="peter"))
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
        character = Character.objects.create(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        game = Game.objects.create(
            status=GameStatus.FINISHED, owner=User.objects.create(username="peter")
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
        character = Character.objects.create(name="Goblin", identifier="goblin")
        hans = User.objects.create(username="hans")
        hans_client = create_player_client(hans)
        peter = User.objects.create(username="peter")
        peter_client = create_player_client(peter)
        game = Game.objects.create(owner=User.objects.create(username="urs"))
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

    def test_creating_a_game_automatically_joins_the_creator(self):
        character = Character.objects.create(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        response = player_client.post(
            reverse("game-list"),
            data={"character": character.pk},
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            [GameStatus.CREATED],
            list(Game.objects.values_list("status", flat=True)),
        )
        self.assertEqual(
            [(player.pk, response.json()["pk"])],
            list(Participation.objects.values_list("player_id", "game_id")),
        )

    def test_creating_a_game_sets_the_creator_as_the_owner(self):
        character = Character.objects.create(name="Goblin", identifier="goblin")
        player = User.objects.create(username="hans")
        player_client = create_player_client(player)
        self.assertEqual(0, Game.objects.count())
        response = player_client.post(
            reverse("game-list"), data={"character": character.pk}
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

        game = Game.objects.create(owner=hans, max_participations=2)
        game.join(hans, Character.objects.create(name="Goblin", identifier="goblin"))
        game.join(peter, Character.objects.create(name="Pirate", identifier="pirate"))
        with self.assertRaises(MaxParticipationsExceeded):
            game.join(urs, Character.objects.create(name="Male", identifier="male"))

    def test_correctly_determines_whose_turn_is_next(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")
        urs = User.objects.create(username="urs")
        bruno = User.objects.create(username="bruno")
        game = Game.objects.create(owner=hans)

        game.join(hans, Character.objects.create(name="Goblin", identifier="goblin"))
        game.join(peter, Character.objects.create(name="Pirate", identifier="pirate"))
        game.join(urs, Character.objects.create(name="Male", identifier="male"))
        game.join(bruno, Character.objects.create(name="Robot", identifier="robot"))

        self.assertEqual(None, game.current_turn)
        self.assertEqual(hans, game.next_turn)

        game.current_turn = peter
        game.save(update_fields=["current_turn"])

        self.assertEqual(peter, game.current_turn)
        self.assertEqual(urs, game.next_turn)

        game.current_turn = bruno
        game.save(update_fields=["current_turn"])

        self.assertEqual(bruno, game.current_turn)
        self.assertEqual(hans, game.next_turn)
        self.assertEqual(hans, game.next_turn)

    def test_creates_only_one_instance_of_the_same_board(self):
        self.assertEqual(
            Board.objects.create(name="board", identifier="board", structure=[]).pk,
            Board.objects.create(name="board", identifier="board", structure=[]).pk,
        )

    def test_moves_some_steps_on_the_board(self):
        hans = User.objects.create(username="hans")
        game = Game.objects.create(owner=hans)
        participation = game.join(
            hans, Character.objects.create(name="Goblin", identifier="goblin")
        )
