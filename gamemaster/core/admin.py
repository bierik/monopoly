from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from ordered_model.admin import OrderedInlineModelAdminMixin, OrderedTabularInline

from core.authentication.models import Player
from core.board.models import Board, Tile
from core.device.models import Device
from core.game.models import Character, Game, Participation


@admin.register(Player)
class PlayerAdmin(UserAdmin):
    pass


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    pass


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    pass


class TileInline(OrderedTabularInline):
    model = Tile
    ordering = ["order"]
    fields = ("identifier", "order", "move_up_down_links", "direction", "texture")
    readonly_fields = (
        "order",
        "move_up_down_links",
    )
    extra = 1


@admin.register(Board)
class BoardAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    inlines = [TileInline]
