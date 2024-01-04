from functools import cached_property

from django.db import models
from django.utils.translation import gettext_lazy as _


class Board(models.Model):
    class Meta:
        verbose_name = "Spielbrett"
        verbose_name_plural = "Spielbretter"

    name = models.TextField(verbose_name="Name")
    root_tile = models.ForeignKey(
        "Tile", verbose_name="Startfeld", on_delete=models.SET_NULL, related_name="+", null=True, blank=True
    )

    def set_root_tile(self, tile):
        self.root_tile = tile
        self.save(update_fields=["root_tile"])


class TileTypes(models.TextChoices):
    SIDE = "SIDE", _("RAND")
    CORNER = "CORNER", _("Ecke")


class Tile(models.Model):
    class Meta:
        verbose_name = "Feld"
        verbose_name_plural = "Felder"

    identifier = models.TextField(verbose_name="Identifier")
    type = models.TextField(verbose_name="Typ", choices=TileTypes.choices)

    board = models.ForeignKey(
        "Board", verbose_name="Spielbrett", on_delete=models.SET_NULL, related_name="tiles", null=True, blank=True
    )
    successor = models.ForeignKey(
        "Tile", verbose_name="Nachfolger", on_delete=models.SET_NULL, related_name="predecessor", null=True, blank=True
    )

    def set_successor(self, tile):
        self.successor = tile
        self.save(update_fields=["successor"])

    # def to_json(self):
    #     node_link_data = pick(json_graph.node_link_data(self), "nodes", "links")
    #     node_link_data["root_node"] = self.root_node
    #     return node_link_data

    def successors(self, num_successors):
        if num_successors == 0:
            return self
        return self.successor.successors(num_successors - 1)
