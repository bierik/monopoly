# Generated by Django 5.0.7 on 2024-07-21 18:56

import uuid

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import django_extensions.db.fields
import statemachine.mixins
from django.conf import settings
from django.db import migrations, models

import core.action.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Board",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField(verbose_name="Name")),
            ],
            options={
                "verbose_name": "Spielbrett",
                "verbose_name_plural": "Spielbretter",
            },
        ),
        migrations.CreateModel(
            name="Character",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(db_index=True, editable=False, verbose_name="order")),
                ("name", models.TextField(verbose_name="Name")),
                ("identifier", models.TextField(verbose_name="Identifier")),
                (
                    "model",
                    models.FileField(
                        upload_to="characters",
                        validators=[django.core.validators.FileExtensionValidator(["gltf"])],
                        verbose_name="3D Modell",
                    ),
                ),
            ],
            options={
                "verbose_name": "Spielfigur",
                "verbose_name_plural": "Spielfiguren",
                "ordering": ("order",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("user_agent", models.TextField()),
            ],
            options={
                "verbose_name": "Gerät",
                "verbose_name_plural": "Geräte",
            },
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Game",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name="created")),
                ("modified", django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name="modified")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("CREATED", "Erstellt"),
                            ("RUNNING", "Läuft"),
                            ("PAUSED", "Pausiert"),
                            ("FINISHED", "Abgeschlossen"),
                        ],
                        default="CREATED",
                        verbose_name="Status",
                    ),
                ),
                ("max_participations", models.PositiveIntegerField(default=4, verbose_name="Maximale Anzahl Teilnahmen")),
                ("initial_balance", models.PositiveIntegerField(default=0, verbose_name="Startkapital")),
                (
                    "board",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="games",
                        to="core.board",
                        verbose_name="Spielbrett",
                    ),
                ),
                (
                    "current_turn",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Am Zug",
                    ),
                ),
                (
                    "device",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="games", to="core.device"),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="games",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Spielleiter",
                    ),
                ),
            ],
            options={
                "verbose_name": "Spiel",
                "verbose_name_plural": "Spiele",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="Tile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(db_index=True, editable=False, verbose_name="order")),
                ("identifier", models.TextField(verbose_name="Identifier")),
                ("type", models.TextField(choices=[("SIDE", "RAND"), ("CORNER", "Ecke")], verbose_name="Typ")),
                (
                    "direction",
                    models.TextField(
                        choices=[
                            ("RIGHT", "Nach rechts"),
                            ("BOTTOM", "Nach unten"),
                            ("LEFT", "Nach links"),
                            ("TOP", "Nach oben"),
                        ],
                        verbose_name="Richtung",
                    ),
                ),
                (
                    "texture",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="textures",
                        validators=[django.core.validators.FileExtensionValidator(["webp"])],
                        verbose_name="Textur",
                    ),
                ),
                ("action", core.action.fields.ActionField(verbose_name="Aktion")),
                (
                    "board",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tiles",
                        to="core.board",
                        verbose_name="Spielbrett",
                    ),
                ),
            ],
            options={
                "verbose_name": "Feld",
                "verbose_name_plural": "Felder",
                "ordering": ("order",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Participation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(db_index=True, editable=False, verbose_name="order")),
                ("balance", models.FloatField(default=0, verbose_name="Saldo")),
                ("state", models.CharField(default="idle")),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participations",
                        to="core.character",
                        verbose_name="Spielfigur",
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participations",
                        to="core.game",
                        verbose_name="Spiel",
                    ),
                ),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Spieler",
                    ),
                ),
                (
                    "current_tile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participations",
                        to="core.tile",
                        verbose_name="Momentanes Spielfeld",
                    ),
                ),
            ],
            options={
                "verbose_name": "Teilnahme",
                "verbose_name_plural": "Teilnahmen",
                "ordering": ("order",),
                "abstract": False,
            },
            bases=(models.Model, statemachine.mixins.MachineMixin),
        ),
    ]