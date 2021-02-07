from django.utils.translation import gettext as _
from polymorphic.models import PolymorphicModel
from game.models.board import Board
from django.db import models


class ActionCard(PolymorphicModel):
    class Meta:
        verbose_name = _("ActionCard")
        verbose_name_plural = _("ActionCards")

    board = models.ForeignKey(Board, on_delete=models.PROTECT)

    def __str__(self):
        return "Actioncard"


class Chance(ActionCard):
    class Meta:
        verbose_name = _("Chance")
        verbose_name_plural = _("Chance")

    def __str__(self):
        return "Chance"


class Chancellery(ActionCard):
    class Meta:
        verbose_name = _("Chancellery")
        verbose_name_plural = _("Chancelleries")

    def __str__(self):
        return "Chancellery"
