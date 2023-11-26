from rest_framework.test import APIClient


def create_player_client(player):
    client = APIClient()
    client.force_authenticate(player)
    return client
