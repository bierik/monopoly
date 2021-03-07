from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from game.models.board import Board
from game.models.game import Game
from game.models.tile import ChancelleryTile, ChanceTile, ColoredTile, SimpleTile, Tile
from game.models.tile_group import TileGroup


@admin.register(Tile)
class TileParentAdmin(PolymorphicParentModelAdmin, OrderedModelAdmin):
    list_display = (
        "__str__",
        "move_up_down_links",
    )
    base_model = Tile
    child_models = (SimpleTile, ChancelleryTile, ChanceTile, ColoredTile)


@admin.register(SimpleTile)
class SimpleTileAdmin(PolymorphicChildModelAdmin):
    base_model = SimpleTile
    show_in_index = True


@admin.register(ChancelleryTile)
class ChancelleryTileAdmin(PolymorphicChildModelAdmin):
    base_model = ChancelleryTile
    show_in_index = True


@admin.register(ChanceTile)
class ChanceTileAdmin(PolymorphicChildModelAdmin):
    base_model = ChanceTile
    show_in_index = True


@admin.register(ColoredTile)
class ColoredTileAdmin(PolymorphicChildModelAdmin):
    base_model = ColoredTile
    show_in_index = True


@admin.register(TileGroup)
class TileGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass
