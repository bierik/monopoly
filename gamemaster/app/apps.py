from django.apps import AppConfig
from statemachine import registry as statemachine_registry

from app.action.action import NoopAction
from app.action.registry import action_registry
from app.game.participation import ParticipationStateMachine
from app.mqtt_client import mqtt_client


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        mqtt_client.connect()
        action_registry.register(NoopAction)
        statemachine_registry.register(ParticipationStateMachine)
        import app.action.built_in_actions  # noqa: F401, PLC0415
