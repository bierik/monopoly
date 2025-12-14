from django.db.models import CharField

from app.action.action import NoopAction
from app.action.exceptions import InvalidActionNameError
from app.action.registry import action_registry


class ActionField(CharField):
    description = "Holds an action from the action registry"

    def from_db_value(self, value, expression, connection):
        if not value:
            return NoopAction
        return action_registry.for_name(value)

    def to_python(self, value):
        if not value:
            return NoopAction
        if not action_registry.exists(value):
            raise InvalidActionNameError
        return action_registry.for_name(value)

    def get_prep_value(self, value):
        if not value:
            return action_registry.get_action_key(NoopAction)
        if not action_registry.exists(value):
            raise InvalidActionNameError
        return action_registry.get_action_key(value)
