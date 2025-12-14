from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from app.authentication.models import Player
from app.game.models import Character


def create_player_client(player):
    client = APIClient()
    client.force_authenticate(player)
    return client


def create_board_client(token):
    client = APIClient()
    client.credentials(**{"HTTP_X-Device-Token": token})
    return client


def create_anonymous_client():
    return APIClient()


def create_player(username="player", password="player"):  # noqa: S107
    player = Player.objects.create(username=username)
    player.set_password(password)
    player.save()
    return player


def inject_device_token(page, device):
    page.evaluate("(token) => window.localStorage.setItem('deviceToken', token)", str(device.token))


with (Path(__file__).parent / "game" / "fixtures" / "Casual_Male.gltf").open("rb") as gltf:
    DEFAULT_CHARACTER_MODEL = gltf.read()


def create_character(name, identifier, **kwargs):
    return Character.objects.create(
        name=name,
        identifier=identifier,
        model=SimpleUploadedFile("model.gltf", DEFAULT_CHARACTER_MODEL, "application/json"),
        **kwargs,
    )
