from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel

from core.action.fields import ActionField


class Board(models.Model):
    name = models.TextField(verbose_name="Name")

    class Meta:
        verbose_name = "Spielbrett"
        verbose_name_plural = "Spielbretter"

    def __str__(self):
        return self.name


class TileTypes(models.TextChoices):
    SIDE = "SIDE", _("RAND")
    CORNER = "CORNER", _("Ecke")


class Direction(models.TextChoices):
    RIGHT = "RIGHT", _("Nach rechts")
    BOTTOM = "BOTTOM", _("Nach unten")
    LEFT = "LEFT", _("Nach links")
    TOP = "TOP", _("Nach oben")


class Tile(OrderedModel, models.Model):
    identifier = models.TextField(verbose_name="Identifier")
    type = models.TextField(verbose_name="Typ", choices=TileTypes)
    direction = models.TextField(verbose_name="Richtung", choices=Direction)
    texture = models.FileField(
        verbose_name="Textur",
        upload_to="textures",
        validators=[FileExtensionValidator(["webp"])],
        null=True,
        blank=True,
    )
    action = ActionField(verbose_name="Aktion")

    board = models.ForeignKey(
        "Board",
        verbose_name="Spielbrett",
        on_delete=models.SET_NULL,
        related_name="tiles",
        null=True,
        blank=True,
    )

    class Meta(OrderedModel.Meta):
        verbose_name = "Feld"
        verbose_name_plural = "Felder"

    def __str__(self):
        return f"{self.identifier} on {self.board.name}"

    def next(self):
        next_tile = super().next()
        return next_tile if next_tile else self.__class__.objects.first()

    def successor(self, num_successors):
        queryset = self.get_ordering_queryset()
        tile_list = list(queryset)
        current_index = tile_list.index(self)
        total_tiles = len(tile_list)

        successor_index = (current_index + num_successors) % total_tiles
        return tile_list[successor_index]

    def successors(self, num_successors):
        tile_list = list(self.get_ordering_queryset())
        current_index = tile_list.index(self)
        total_tiles = len(tile_list)

        for i in range(1, num_successors + 1):
            successor_index = (current_index + i) % total_tiles
            yield tile_list[successor_index]

    def call_action(self, participation, trigger):
        self.action()(participation=participation, trigger=trigger)
