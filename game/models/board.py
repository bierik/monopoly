from django.db import models
from django.utils.translation import gettext as _

from game.models.game import Game


class Board(models.Model):
    class Meta:
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")

    game = models.OneToOneField(Game, on_delete=models.PROTECT)

    def __str__(self):
        return "Board"
