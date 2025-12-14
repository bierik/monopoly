from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from ordered_model.models import OrderedModel
from statemachine.mixins import MachineMixin

from app.action.trigger import Triggers
from app.exceptions import AlreadyParticipantError
from app.exceptions import GameStartError
from app.exceptions import JoinStartedGameError
from app.exceptions import LobbyNotReadyError
from app.exceptions import MaxParticipationsError
from app.exceptions import NotPlayersTurnError
from app.exceptions import ParticipationBlockedError
from app.exceptions import RollDiceNotAllowedError
from app.exceptions import SameCharacterError
from app.game.dice import roll_dice
from app.game.participation import ParticipationStates
from app.mqtt_client import mqtt_client
from app.storage.storages import ModelStorage
from app.storage.storages import get_s3_file_path
from app.validators import validate_gltf


class GameStatus(models.TextChoices):
    CREATED = "CREATED", _("Erstellt")
    RUNNING = "RUNNING", _("Läuft")
    PAUSED = "PAUSED", _("Pausiert")
    FINISHED = "FINISHED", _("Abgeschlossen")


accept_start_status = [GameStatus.CREATED, GameStatus.RUNNING]


class Character(OrderedModel, models.Model):
    name = models.TextField(verbose_name=_("Name"))
    identifier = models.TextField(verbose_name=_("Identifier"))
    model = models.FileField(
        verbose_name=_("3D Modell"),
        validators=[FileExtensionValidator(["gltf"]), validate_gltf],
        upload_to=get_s3_file_path,
        storage=ModelStorage,
    )

    class Meta(OrderedModel.Meta):
        verbose_name = _("Spielfigur")
        verbose_name_plural = _("Spielfiguren")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().full_clean()
        return super().save(*args, **kwargs)


class GameManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                num_participations=models.Count("participations"),
                is_lobby_full=models.Case(
                    models.When(num_participations__gte=models.F("max_participations"), then=True),
                    default=False,
                    output_field=models.BooleanField(),
                ),
            )
        )

    def owned(self, owner):
        return self.get_queryset().filter(owner=owner)


class Game(TimeStampedModel, models.Model):
    status = models.CharField(
        choices=GameStatus,
        default=GameStatus.CREATED,
        verbose_name=_("Status"),
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
    max_participations = models.PositiveIntegerField(verbose_name=_("Maximale Anzahl Teilnahmen"), default=4)
    initial_balance = models.PositiveIntegerField(verbose_name=_("Startkapital"), default=0)
    board = models.ForeignKey("Board", verbose_name=_("Spielbrett"), on_delete=models.CASCADE, related_name="games")
    device = models.ForeignKey("Device", on_delete=models.PROTECT, related_name="games")

    objects = GameManager()

    class Meta:
        verbose_name = _("Spiel")
        verbose_name_plural = _("Spiele")
        ordering = ["-created"]

    def __str__(self):
        return self.status

    def _check_can_join(self, player, character):
        if self.participations.count() == self.max_participations:
            raise MaxParticipationsError
        if self.participations.filter(player=player).exists():
            raise AlreadyParticipantError
        if self.status != GameStatus.CREATED:
            raise JoinStartedGameError
        if self.participations.filter(character=character).exists():
            raise SameCharacterError

    def _check_can_start(self):
        if self.participations.count() != self.max_participations:
            raise LobbyNotReadyError
        if self.status not in accept_start_status:
            raise GameStartError

    def join(self, player, character, balance=None):
        balance = balance or self.initial_balance
        self._check_can_join(player, character)
        return Participation.objects.create(
            game=self,
            player=player,
            character=character,
            balance=balance,
            current_tile=self.board.tiles.first(),
        )

    @property
    def next_turn(self):
        if not self.current_turn:
            return self.participations.first().player
        return self.participations.get(player=self.current_turn).next().player

    def participation_for_player(self, player):
        return Participation.objects.get(game=self, player=player)

    def give_turn_to(self, player):
        self.current_turn = player
        self.save(update_fields=["current_turn"])

    def hand_over_turn(self):
        self.give_turn_to(self.next_turn)

    def start(self):
        self._check_can_start()
        self.status = GameStatus.RUNNING
        self.save(update_fields=["status"])
        self.hand_over_turn()


@receiver(signals.post_save, sender=Game)
def game_changed(created, instance, **kwargs):
    if created:
        mqtt_client.publish_game_created(instance)
    else:
        mqtt_client.publish_game_changed(instance)


class Participation(OrderedModel, models.Model, MachineMixin):
    order_with_respect_to = "game"

    state_machine_name = "app.game.participation.ParticipationStateMachine"

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
        related_name="participations",
    )
    balance = models.FloatField(
        verbose_name=_("Saldo"),
        default=0,
    )
    state = models.CharField(default=ParticipationStates.IDLE.value)
    is_blocked = models.BooleanField(verbose_name=_("Blockiert"), default=False)

    class Meta(OrderedModel.Meta):
        verbose_name = _("Teilnahme")
        verbose_name_plural = _("Teilnahmen")

    def __str__(self):
        return f"{self.player.username} with {self.character.identifier} on {self.current_tile.identifier}"

    def next(self):
        next_participation = super().next()
        return next_participation if next_participation else self.__class__.objects.first()

    def previous(self):
        prev = super().previous()
        return prev if prev else self.__class__.objects.last()

    @property
    def is_players_turn(self):
        return self.game.current_turn == self.player

    def move(self, steps):
        if not self.is_players_turn:
            raise NotPlayersTurnError
        if not self.state == ParticipationStates.IDLE.value:
            raise RollDiceNotAllowedError
        if self.is_blocked:
            raise ParticipationBlockedError
        for tile in self.current_tile.successors(steps):
            tile.call_action(participation=self, trigger=Triggers.TRAVERSED)
        self.current_tile = self.current_tile.successor(steps)
        self.save(update_fields=["current_tile"])
        self.current_tile.call_action(participation=self, trigger=Triggers.LANDED_ON)
        self.statemachine.move()
        mqtt_client.publish_character_moved(self)

    def move_random(self):
        self.move(roll_dice()[0])

    def end_turn(self):
        self.statemachine.end_turn()
        self.game.hand_over_turn()

    def block(self):
        self.is_blocked = True
        self.save(update_fields=["is_blocked"])

    def release(self):
        self.is_blocked = False
        self.save(update_fields=["is_blocked"])


@receiver(signals.post_save, sender=Participation)
def participation_changed(created, instance, **kwargs):
    if created:
        mqtt_client.publish_participation_created(instance)
    else:
        mqtt_client.publish_participation_changed(instance)
