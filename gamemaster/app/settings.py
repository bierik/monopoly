from functools import cached_property
from pathlib import Path
from urllib.parse import urlparse
from warnings import filterwarnings

from configurations import Configuration
from configurations import values


filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")


class Base(Configuration):
    BASE_DIR = Path(__file__).resolve().parent.parent
    BASE_URL = values.Value()
    BOARD_URL = values.Value()
    PLAYER_URL = values.Value()

    @cached_property
    def ALLOWED_HOSTS(self):  # noqa: N802
        return [
            urlparse(self.BASE_URL).hostname,
            urlparse(self.BOARD_URL).hostname,
            urlparse(self.PLAYER_URL).hostname,
            *values.ListValue([], environ_name="ALLOWED_HOSTS"),
        ]

    DATABASE_HOST = "db"
    DATABASE_NAME = "postgres"
    DATABASE_PASSWORD = "secret"  # noqa: S105
    DATABASE_PORT = 5432
    DATABASE_USER = "postgres"
    APPEND_SLASH = False
    LOGGING_LEVEL = "WARNING"
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
        "storages",
        "app",
        "drf_spectacular",
    ]
    MIDDLEWARE = [
        "servestatic.middleware.ServeStaticMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "app.device.token_middleware.DeviceTokenMiddleware",
    ]
    ROOT_URLCONF = "app.urls"
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
    STATIC_ROOT = BASE_DIR / "static"
    STATIC_URL = "/api/static/"

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

    @property
    def DATABASES(self):  # noqa: N802
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": self.DATABASE_NAME,
                "USER": self.DATABASE_USER,
                "PASSWORD": self.DATABASE_PASSWORD,
                "HOST": self.DATABASE_HOST,
                "PORT": self.DATABASE_PORT,
                "ATOMIC_REQUESTS": True,
                "CONN_MAX_AGE": 60,
                "CONN_HEALTH_CHECKS": True,
            }
        }

    @property
    def CSRF_TRUSTED_ORIGINS(self):  # noqa: N802
        return [self.BASE_URL, self.BOARD_URL, self.PLAYER_URL]

    @property
    def LOGGING(self):  # noqa: N802
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"verbose": {"format": "{levelname:<8}  {name} - {message}", "style": "{"}},
            "handlers": {"stream": {"class": "logging.StreamHandler", "formatter": "verbose"}},
            "loggers": {"": {"handlers": ["stream"], "level": self.LOGGING_LEVEL}},
        }

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

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "servestatic.storage.CompressedManifestStaticFilesStorage",
        },
    }

    AWS_S3_ENDPOINT_URL = values.Value("", environ_prefix="")
    AWS_S3_ACCESS_KEY_ID = values.Value("", environ_prefix="")
    AWS_S3_SECRET_ACCESS_KEY = values.Value("", environ_prefix="")
    AWS_STORAGE_BUCKET_NAME = values.Value("", environ_prefix="")

    @property
    def SPECTACULAR_SETTINGS(self):  # noqa: N802
        return {
            "TITLE": "Monopoly gamemaster",
            "DESCRIPTION": "Implements monopoly game rules",
            "VERSION": "1.0.0",
            "SERVE_INCLUDE_SCHEMA": False,
            "SERVERS": [
                {"url": self.BASE_URL, "description": "Dev"},
            ],
        }

    LANGUAGE_CODE = "de-CH"
    LANGUAGES = [("de-CH", "Deutsch")]
    LOCALE_PATHS = [BASE_DIR / "app/locale"]
    TIME_ZONE = "Europe/Zurich"
    USE_TZ = True
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
    AUTH_USER_MODEL = "app.Player"
    MQTT_HOST = "mosquitto"
    MQTT_PORT = 1883

    VALIDATE_GLTF = True
    GLTF_ANIMATIONS = ["Idle", "Walk", "Run"]


class Development(Base):
    BASE_URL = "https://gamemaster.local:8000"
    BOARD_URL = "https://board.local:8000"
    PLAYER_URL = "https://player.local:8000"
    SECRET_KEY = "secret"  # noqa: S105
    DEBUG = True

    AWS_S3_ENDPOINT_URL = "https://storage.local:9000"
    AWS_S3_ACCESS_KEY_ID = "admin"
    AWS_S3_SECRET_ACCESS_KEY = "password"  # noqa: S105
    AWS_STORAGE_BUCKET_NAME = "monopoly"
    AWS_S3_VERIFY = False

    LOGGING_LEVEL = "INFO"


class Testing(Base):
    DEBUG = True
    SECRET_KEY = "testing"  # noqa: S105

    LOGGING_LEVEL = "INFO"
    DATABASE_PORT = 20000

    VALIDATE_GLTF = False

    MQTT_HOST = "localhost"
