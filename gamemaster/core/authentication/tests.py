import pydash
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.game.models import Game
from core.testutils import create_player_client

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    def test_list_all_games_for_a_user(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")

        hans_game = Game.objects.create(owner=hans)
        Game.objects.create(owner=peter)

        player_client = create_player_client(hans)
        response = player_client.get(reverse("authentication-games"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([hans_game.pk], pydash.pluck(response.json(), "pk"))
