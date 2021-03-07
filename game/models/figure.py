from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _

from game.models.tile import Tile

Player = get_user_model()


class Figure(models.Model):
    class Meta:
        verbose_name = _("Figure")
        verbose_name_plural = _("Figures")

    tile = models.ForeignKey(Tile, on_delete=models.PROTECT, related_name="figures")
    player = models.OneToOneField(Player, on_delete=models.PROTECT, related_name="figure")

    def move_to(self, tile):
        self.tile = tile
        self.save()

    def __str__(self):
        return "Figure"
