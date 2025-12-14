import inspect

from app.action.exceptions import ActionNotFoundError
from app.action.exceptions import InvalidActionDeclarationError
from app.action.exceptions import InvalidActionTriggersError
from app.action.trigger import Triggers


class ActionRegistry:
    store = {}

    def register(self, action_class):
        superclass_names = [subclass.__name__ for subclass in action_class.__mro__]
        if "Action" not in superclass_names:
            raise InvalidActionDeclarationError
        if len(set(action_class.triggers) - set(Triggers.__members__.values())) != 0:
            raise InvalidActionTriggersError
        self.store[action_class.__name__] = action_class

    def get_action_key(self, name):
        if isinstance(name, str):
            return name
        if inspect.isclass(name):
            return name.__name__
        return name

    def exists(self, name):
        return self.get_action_key(name) in self.store

    def for_name(self, name):
        name = self.get_action_key(name)
        if name not in self.store:
            raise ActionNotFoundError
        return self.store[name]

    def call_for_name(self, name, **kwargs):
        self.for_name(name)()(**kwargs)

    def clear(self):
        self.store = {}


action_registry = ActionRegistry()


def register():
    def wrapper(action_class):
        action_registry.register(action_class)
        return action_class

    return wrapper
