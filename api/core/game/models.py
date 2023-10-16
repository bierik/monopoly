from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from ordered_model.models import OrderedModel
from rest_framework.exceptions import ValidationError

from core.board_structures import monopoly
from core.game.turn import MoveForward


class AlreadyParticipantException(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Player is already participating",
            code="player_already_participating",
        )


class JoinStartedGameException(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Game has already started",
            code="game_has_already_started",
        )


class SameCharacterException(ValidationError):
    def __init__(self):
        super().__init__(
            detail="The characters have to be unique per game",
            code="unique_character",
        )


class MaxParticipationsExceeded(ValidationError):
    def __init__(self):
        super().__init__(
            detail="The maximum amount of participations is exceeded.",
            code="max_participations_exeeded",
        )


class GameStatus(models.TextChoices):
    CREATED = "CREATED", _("Erstellt")
    RUNNING = "RUNNING", _("Läuft")
    PAUSED = "PAUSED", _("Pausiert")
    FINISHED = "FINISHED", _("Abgeschlossen")


class Character(models.Model):
    class Meta:
        verbose_name = _("Spielfigur")
        verbose_name_plural = _("Spielfiguren")
        ordering = ["name"]

    name = models.TextField(verbose_name=_("Name"))
    identifier = models.TextField(
        verbose_name=_("Identifier"), help_text=_("Muss einem gltf Modell entsprechen.")
    )


class GameManager(models.Manager):
    def create(self, **kwargs):
        kwargs["board"] = Board.create_monopoly_board()
        return super().create(**kwargs)


class Game(TimeStampedModel):
    class Meta:
        verbose_name = _("Spiel")
        verbose_name_plural = _("Spiele")
        ordering = ["-created"]

    status = models.CharField(
        choices=GameStatus.choices, default=GameStatus.CREATED, verbose_name=_("Status")
    )
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
    max_participations = models.IntegerField(
        verbose_name=_("Maximale Anzahl Teilnahmen"), default=4
    )
    board = models.OneToOneField(
        "Board",
        on_delete=models.CASCADE,
        verbose_name=_("Spielbrett"),
        related_name="game",
    )

    objects = GameManager()

    def join(self, player, character, balance=0):
        if self.participations.filter(player=player).exists():
            raise AlreadyParticipantException()
        if self.status != GameStatus.CREATED:
            raise JoinStartedGameException()
        if self.participations.filter(character=character).exists():
            raise SameCharacterException()
        if self.participations.count() == self.max_participations:
            raise MaxParticipationsExceeded()
        return Participation.objects.create(
            game=self,
            player=player,
            character=character,
            balance=balance,
        )

    @property
    def next_turn(self):
        if not self.current_turn:
            return self.participations.first().player
        return self.participations.get(player=self.current_turn).next().player


class Turn(TimeStampedModel):
    class Meta:
        verbose_name = _("Spielzug")
        verbose_name_plural = _("Spielzüge")

    logic = models.TextField(verbose_name=_("Logik"))
    logic_params = models.JSONField(verbose_name=_("Logikparameter"))
    participation = models.ForeignKey(
        "Participation",
        on_delete=models.CASCADE,
        verbose_name=_("Teilnahme"),
        related_name="turns",
    )


class BoardManager(models.Manager):
    def create(self, **kwargs):
        try:
            return self.get(identifier=kwargs.get("identifier"))
        except Board.DoesNotExist:
            return super().create(**kwargs)


class Board(models.Model):
    class Meta:
        verbose_name = _("Spielbrett")
        verbose_name_plural = _("Spielbretter")

    name = models.CharField(verbose_name=_("Name"))
    identifier = models.CharField(verbose_name=_("Identifier"))
    structure = models.JSONField(verbose_name=_("Aufbau"))

    objects = BoardManager()

    @classmethod
    def create_monopoly_board(cls):
        return cls.objects.create(
            name="Monopoly", structure=monopoly, identifier="monopoly"
        )


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
    current_tile = models.TextField(
        verbose_name=_("Momentanes Spielfeld"),
        default="start",
        help_text=_("Muss einem Spielfeld auf dem Board entsprechen."),
    )
    balance = models.FloatField(verbose_name=_("Saldo"))

    def next(self):
        next = super().next()
        return next if next else self.__class__.objects.first()

    def previous(self):
        prev = super().previous()
        return prev if prev else self.__class__.objects.last()

    def move_forward(self, steps):
        turn = Turn.objects.create(
            logic=MoveForward, logic_params={"steps": steps}, participation=self
        )
        turn.run()

    def make_turn(self, turn):
        turn.run(self)
