from django.db.utils import IntegrityError


class InvalidActionDeclarationError(TypeError):
    pass


class ActionNotFoundError(KeyError):
    pass


class InvalidActionNameError(IntegrityError):
    pass


class InvalidActionTriggersError(ValueError):
    pass
