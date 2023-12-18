from django.apps import AppConfig

from core.board.monopoly import monopoly
from core.board.registry import board_registry
from core.mqtt_client import mqtt_client


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        board_registry.register(monopoly, "monopoly")
        mqtt_client.connect()
