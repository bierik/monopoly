from django.db import models
from django.utils.translation import gettext as _

from game.models.board import Board


class TileGroup(models.Model):
    class Meta:
        verbose_name = _("Tilegroup")
        verbose_name_plural = _("Tilegroups")

    board = models.ForeignKey(Board, on_delete=models.PROTECT, related_name="tile_groups")

    def __str__(self):
        return "Tilegroup"
