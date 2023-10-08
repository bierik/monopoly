from django.apps import AppConfig
from statemachine import registry as statemachine_registry

from core.action.action import NoopAction
from core.action.registry import action_registry
from core.game.participation import ParticipationStateMachine
from core.mqtt_client import mqtt_client


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        mqtt_client.connect()
        action_registry.register(NoopAction)
        statemachine_registry.register(ParticipationStateMachine)
        import core.action.built_in_actions  # noqa: F401
