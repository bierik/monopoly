from pathlib import Path

from configurations import Configuration


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
    }

    LANGUAGE_CODE = "de-ch"
    TIME_ZONE = "UTC"
    USE_TZ = True

    STATIC_URL = "static/"

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    AUTH_USER_MODEL = "core.Player"

    VALIDATE_GLTF = True
    GLTF_ANIMATIONS = ["Idle", "Walk", "Run"]


class Development(Base):
    SECRET_KEY = "secret"
    DEBUG = True

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "db",
            "PORT": "5432",
        }
    }

    def MEDIA_ROOT(self):
        return self.BASE_DIR / "media"

    MEDIA_URL = "/media/"


class Testing(Base):
    SECRET_KEY = "testing"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": "5010",
        }
    }
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.memory.InMemoryStorage",
        },
    }
    VALIDATE_GLTF = False
