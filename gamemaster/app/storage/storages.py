from pathlib import Path
from uuid import uuid4

from storages.backends.s3boto3 import S3Boto3Storage


def get_s3_file_path(instance, filename):
    uuid = uuid4().hex
    return str(Path(*[uuid[i : i + 2] for i in range(0, 6, 2)], uuid[6:], filename))


class ModelStorage(S3Boto3Storage):
    location = "models"


class TextureStorage(S3Boto3Storage):
    location = "textures"
