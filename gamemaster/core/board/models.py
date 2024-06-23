from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel


class Board(models.Model):
    class Meta:
        verbose_name = "Spielbrett"
        verbose_name_plural = "Spielbretter"

    name = models.TextField(verbose_name="Name")

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


class Tile(OrderedModel):
    class Meta:
        verbose_name = "Feld"
        verbose_name_plural = "Felder"
        ordering = ["order"]

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

    board = models.ForeignKey(
        "Board",
        verbose_name="Spielbrett",
        on_delete=models.SET_NULL,
        related_name="tiles",
        null=True,
        blank=True,
    )

    def next(self):
        next = super().next()
        return next if next else self.__class__.objects.first()

    def successor(self, num_successors):
        num_successors = num_successors % self.board.tiles.count()
        if num_successors == 0:
            return self

        return self.get_ordering_queryset().above_instance(self)[num_successors - 1]
