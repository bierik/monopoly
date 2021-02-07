from django.db import models
from ordered_model.models import OrderedModel
from django.utils.translation import gettext as _
from game.models.tile_group import TileGroup


class Tile(OrderedModel):
    class Meta:
        verbose_name = _("Tile")
        verbose_name_plural = _("Tiles")

    tile_group = models.ForeignKey(TileGroup, on_delete=models.PROTECT, related_name="tiles")
    title = models.CharField(verbose_name=_("Feldtitel"), max_length=4096)

    def __str__(self):
        return "Tile"
