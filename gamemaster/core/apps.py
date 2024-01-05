from django.apps import AppConfig

from core.mqtt_client import mqtt_client


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        mqtt_client.connect()
