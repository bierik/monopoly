from pathlib import Path
from warnings import filterwarnings

from configurations import Configuration

filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")


class Base(Configuration):
    BASE_DIR = Path(__file__).resolve().parent

    ALLOWED_HOSTS = ["*"]

    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_extensions",
        "drf_standardized_errors",
        "ordered_model",
        "core",
        "drf_spectacular",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "core.device.token_middleware.DeviceTokenMiddleware",
    ]

    ROOT_URLCONF = "urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    ASGI_APPLICATION = "asgi.application"

    REST_FRAMEWORK = {
        "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }

    SPECTACULAR_SETTINGS = {
        "TITLE": "Monopoly gamemaster",
        "DESCRIPTION": "Implements monopoly game rules",
        "VERSION": "1.0.0",
        "SERVE_INCLUDE_SCHEMA": False,
    }

    LANGUAGE_CODE = "de-ch"
    TIME_ZONE = "UTC"
    USE_TZ = True

    STATIC_URL = "gamemaster/static/"

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    AUTH_USER_MODEL = "core.Player"

    VALIDATE_GLTF = True
    GLTF_ANIMATIONS = ["Idle", "Walk", "Run"]

    MQTT_HOST = "mosquitto"
    MQTT_PORT = 1883


class Development(Base):
    SECRET_KEY = "secret"  # noqa: S105
    DEBUG = True

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "db",
            "PORT": "5432",
        },
    }

    def MEDIA_ROOT(self):  # noqa: N802
        return self.BASE_DIR / "media"

    MEDIA_URL = "/media/"


class Testing(Base):
    DEBUG = True
    SECRET_KEY = "testing"  # noqa: S105

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": "20000",
        },
    }
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    VALIDATE_GLTF = False
    MEDIA_URL = "/media/"

    MQTT_HOST = "localhost"
    MQTT_PORT = 1883
