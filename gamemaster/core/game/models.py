import pydash
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from ordered_model.models import OrderedModel
from pygltflib import GLTF2

from core.game.exceptions import (
    AlreadyParticipantException,
    GameStartException,
    JoinStartedGameException,
    LobbyNotReadyException,
    MaxParticipationsExceeded,
    SameCharacterException,
)
from core.mqtt_client import mqtt_client


class GameStatus(models.TextChoices):
    CREATED = "CREATED", _("Erstellt")
    RUNNING = "RUNNING", _("Läuft")
    PAUSED = "PAUSED", _("Pausiert")
    FINISHED = "FINISHED", _("Abgeschlossen")

    accept_start_status = [CREATED, RUNNING]


class MissingAnimationsException(ValidationError):
    def __init__(self):
        super().__init__(
            {
                "model": _("Missing animations on gltf model. Necessary animations: {animations}").format(
                    animations=", ".join(settings.GLTF_ANIMATIONS)
                )
            },
            "missing_animations",
        )


class Character(models.Model):
    class Meta:
        verbose_name = _("Spielfigur")
        verbose_name_plural = _("Spielfiguren")
        ordering = ["name"]

    name = models.TextField(verbose_name=_("Name"))
    identifier = models.TextField(verbose_name=_("Identifier"))
    model = models.FileField(
        verbose_name=_("3D Modell"),
        validators=[FileExtensionValidator(["gltf"])],
        upload_to="characters",
    )

    def save(self, *args, **kwargs):
        super().full_clean()
        return super().save(*args, **kwargs)

    def validate_gltf(self):
        self.model.file.seek(0)
        gltf = GLTF2.from_json(self.model.file.read())
        animation_names = set(pydash.pluck(gltf.animations, "name"))

        if not set(settings.GLTF_ANIMATIONS).issubset(animation_names):
            raise MissingAnimationsException()

    def clean(self):
        super().clean_fields()
        if settings.VALIDATE_GLTF:
            self.validate_gltf()


class GameManager(models.Manager):
    def owned(self, owner):
        return self.get_queryset().filter(owner=owner)


class Game(TimeStampedModel):
    class Meta:
        verbose_name = _("Spiel")
        verbose_name_plural = _("Spiele")
        ordering = ["-created"]

    objects = GameManager()

    status = models.CharField(choices=GameStatus.choices, default=GameStatus.CREATED, verbose_name=_("Status"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Spielleiter"),
        related_name="games",
    )
    current_turn = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Am Zug"),
        related_name="+",
    )
    max_participations = models.IntegerField(verbose_name=_("Maximale Anzahl Teilnahmen"), default=4)
    board = models.ForeignKey("Board", verbose_name=_("Spielbrett"), on_delete=models.CASCADE)

    def join(self, player, character, balance=0):
        if self.participations.count() == self.max_participations:
            raise MaxParticipationsExceeded()
        if self.participations.filter(player=player).exists():
            raise AlreadyParticipantException()
        if self.status != GameStatus.CREATED:
            raise JoinStartedGameException()
        if self.participations.filter(character=character).exists():
            raise SameCharacterException()
        participation = Participation.objects.create(
            game=self,
            player=player,
            character=character,
            balance=balance,
            current_tile=self.board.tiles.first(),
        )
        mqtt_client.publish(f"game/{self.pk}/joined", {"game_id": self.pk})
        return participation

    @property
    def next_turn(self):
        if not self.current_turn:
            return self.participations.first().player
        return self.participations.get(player=self.current_turn).next().player

    def give_turn_to(self, player):
        self.current_turn = player
        self.save(update_fields=["current_turn"])

    def hand_over_turn(self):
        self.give_turn_to(self.next_turn)

    def start(self):
        if self.participations.count() != self.max_participations:
            raise LobbyNotReadyException()
        if self.status not in GameStatus.accept_start_status:
            raise GameStartException()
        self.status = GameStatus.RUNNING
        self.save(update_fields=["status"])
        mqtt_client.publish(f"game/{self.pk}/started", {"game_id": self.pk})


class Participation(OrderedModel):
    class Meta(OrderedModel.Meta):
        verbose_name = _("Teilnahme")
        verbose_name_plural = _("Teilnahmen")

    order_with_respect_to = "game"

    game = models.ForeignKey(
        "Game",
        on_delete=models.CASCADE,
        verbose_name=_("Spiel"),
        related_name="participations",
    )
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Spieler"),
        related_name="participations",
    )
    character = models.ForeignKey(
        "Character",
        on_delete=models.CASCADE,
        verbose_name=_("Spielfigur"),
        related_name="participations",
    )
    current_tile = models.ForeignKey(
        "Tile",
        verbose_name=_("Momentanes Spielfeld"),
        on_delete=models.CASCADE,
    )
    balance = models.FloatField(verbose_name=_("Saldo"))

    def next(self):
        next = super().next()
        return next if next else self.__class__.objects.first()

    def previous(self):
        prev = super().previous()
        return prev if prev else self.__class__.objects.last()

    @property
    def is_players_turn(self):
        return self.game.current_turn == self.player

    def move(self, steps):
        self.current_tile = self.current_tile.successor(steps)
        self.save(update_fields=["current_tile"])
