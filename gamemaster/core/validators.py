import pydash
from django.conf import settings
from pygltflib import GLTF2

from core.action.action import ActionContextSerializer
from core.exceptions import ActionContextSchemaMismatchError, MissingAnimationsError


def validate_gltf(model):
    if not settings.VALIDATE_GLTF:
        return
    model.file.seek(0)
    gltf = GLTF2.from_json(model.file.read())
    animation_names = set(pydash.pluck(gltf.animations, "name"))
    if not set(settings.GLTF_ANIMATIONS).issubset(animation_names):
        raise MissingAnimationsError


def validate_action_context(action_context):
    serializer = ActionContextSerializer(data=action_context)
    try:
        serializer.is_valid(raise_exception=True)
    except Exception as e:
        raise ActionContextSchemaMismatchError from e
