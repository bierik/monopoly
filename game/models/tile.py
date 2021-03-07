from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from ordered_model.models import (OrderedModel, OrderedModelManager,
                                  OrderedModelQuerySet)
from polymorphic.models import PolymorphicManager, PolymorphicModel
from polymorphic.query import PolymorphicQuerySet

from game.models.tile_group import TileGroup


class TileQuerySet(PolymorphicQuerySet, OrderedModelQuerySet):
    pass


class TileManager(OrderedModelManager, PolymorphicManager):
    queryset_class = TileQuerySet


class Tile(PolymorphicModel, OrderedModel):
    tile_group = models.ForeignKey(TileGroup, on_delete=models.PROTECT, related_name="tiles")
    title = models.CharField(verbose_name=_("Fieldtitle"), max_length=4096, null=True)
    is_corner = models.BooleanField(verbose_name=_("Is a corner"), default=False)
    order_with_respect_to = "tile_group__board"

    objects = TileManager()

    def save(self, *args, **kwargs):
        if Tile.objects.filter(is_corner=True).count() == 4:
            raise ValidationError(_("There are only four corner tiles allowed"))
        if Tile.objects.filter(tile_group=self.tile_group).not_instance_of(self.__class__).count() != 0:
            raise ValidationError(_("This tile is not allowed"))
        super().save(*args, **kwargs)


class SimpleTile(Tile):
    class Meta:
        verbose_name = _("Tile")
        verbose_name_plural = _("Tiles")

    subtitle = models.CharField(verbose_name=_("Fieldsubtitle"), max_length=4096, null=True)

    def __str__(self):
        return f"SimpleTile: {self.title}"


class ColoredTile(Tile):
    class Meta:
        verbose_name = _("Tile")
        verbose_name_plural = _("Tiles")

    color = ColorField(format="hex", verbose_name=_("Color"), default="#FF0000")
    subtitle = models.CharField(verbose_name=_("Fieldsubtitle"), max_length=4096, null=True)

    def __str__(self):
        return f"ColoredTile: {self.title}, {self.color}"


class ChanceTile(Tile):
    class Meta:
        verbose_name = _("Chance Tile")
        verbose_name_plural = _("Chance Tiles")

    def __str__(self):
        return f"ChanceTile: {self.title}"


class ChancelleryTile(Tile):
    class Meta:
        verbose_name = _("Chancellery Tile")
        verbose_name_plural = _("Chancellery Tiles")

    def __str__(self):
        return f"ChancelleryTile: {self.title}"
