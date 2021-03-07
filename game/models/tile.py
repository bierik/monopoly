from django.db import models
from ordered_model.models import OrderedModelManager
from ordered_model.models import OrderedModel
from django.utils.translation import gettext as _
from game.models.tile_group import TileGroup
from django.core.exceptions import ValidationError


class TileManager(OrderedModelManager):
    def create(self, **kwargs):
        self.model.clean()
        tile = super().create(**kwargs)
        return tile


class Tile(OrderedModel):
    class Meta:
        verbose_name = _("Tile")
        verbose_name_plural = _("Tiles")

    tile_group = models.ForeignKey(TileGroup, on_delete=models.PROTECT, related_name="tiles")
    title = models.CharField(verbose_name=_("Feldtitel"), max_length=4096)
    is_corner = models.BooleanField(verbose_name=_("Ist Ecke"), default=False)

    objects = TileManager()

    @classmethod
    def clean(cls):
        if cls.objects.filter(is_corner=True).count() == 4:
            raise ValidationError(_("There are only four corner tiles allowed"))

    def __str__(self):
        return "Tile"
