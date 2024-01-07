from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from ordered_model.admin import OrderedInlineModelAdminMixin, OrderedTabularInline

from core.authentication.models import Player
from core.board.models import Board, Tile
from core.device.models import Device
from core.game.models import Character, Game, Participation


@admin.register(Player)
class PlayerAdmin(UserAdmin):
    list_display = ["username", "get_full_name"]


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ["identifier", "name"]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["token", "user_agent"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["board", "owner"]


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ["game", "player", "character"]


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
    list_display = ("name",)
