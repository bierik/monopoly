import pydash
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.board.models import Board
from core.device.models import Device
from core.game.models import Game
from core.testutils import create_player_client

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    def test_list_all_games_for_a_user(self):
        hans = User.objects.create(username="hans")
        peter = User.objects.create(username="peter")

        hans_game = Game.objects.create(owner=hans, board=Board.objects.create(name="dummy"), device=Device.objects.create())
        Game.objects.create(owner=peter, board=Board.objects.create(name="dummy"), device=Device.objects.create())

        player_client = create_player_client(hans)
        response = player_client.get(reverse("authentication-games"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([hans_game.pk], pydash.pluck(response.json(), "pk"))

    def test_logs_in_user(self):
        client = APIClient()

        hans = User.objects.create(username="hans", first_name="Hans", last_name="Müller")
        hans.set_password("secret")
        hans.save()

        response = client.post(reverse("login"))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(
            {
                "errors": [
                    {
                        "attr": None,
                        "code": "authentication_failed",
                        "detail": "Incorrect authentication credentials.",
                    },
                ],
                "type": "client_error",
            },
            response.json(),
        )

        response = client.post(reverse("login"), data={"username": "peter"})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(
            {
                "errors": [
                    {
                        "attr": None,
                        "code": "authentication_failed",
                        "detail": "Incorrect authentication credentials.",
                    },
                ],
                "type": "client_error",
            },
            response.json(),
        )

        response = client.post(reverse("login"), data={"username": "hans", "password": "wrong"})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(
            {
                "errors": [
                    {
                        "attr": None,
                        "code": "authentication_failed",
                        "detail": "Incorrect authentication credentials.",
                    },
                ],
                "type": "client_error",
            },
            response.json(),
        )

        response = client.post(reverse("login"), data={"username": "hans", "password": "secret"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("hans", response.json()["username"])

    def test_logout(self):
        client = APIClient()

        hans = User.objects.create(username="hans")
        client.force_authenticate(hans)

        response = client.post(reverse("logout"))
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_get_logged_in_user(self):
        client = APIClient()

        response = client.get(reverse("authentication-me"))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        hans = User.objects.create(username="hans")
        client.force_authenticate(hans)

        response = client.get(reverse("authentication-me"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("hans", response.json()["username"])
