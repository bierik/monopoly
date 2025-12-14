from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import mark_safe
from ordered_model.admin import OrderedInlineModelAdminMixin
from ordered_model.admin import OrderedTabularInline

from app.authentication.models import Player
from app.board.models import Board
from app.board.models import Tile
from app.device.models import Device
from app.game.models import Character
from app.game.models import Game
from app.game.models import Participation


@admin.register(Player)
class PlayerAdmin(UserAdmin):
    list_display = ["username", "get_full_name"]
    list_filter = []


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ["identifier", "name"]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["token", "user_agent"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["board", "owner"]
    list_filter = ["owner"]


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ["game", "player", "character"]
    list_filter = ["player", "character"]


class TileInline(OrderedTabularInline):
    def texture_preview(self, obj):
        return mark_safe(f'<img src="{obj.texture.url}" style="max-height: 100px; max-width: 100px;" />')  # noqa: S308

    texture_preview.allow_tags = True
    texture_preview.short_description = "Texture Preview"

    model = Tile
    ordering = ["order"]
    fields = ("identifier", "move_up_down_links", "direction", "texture", "texture_preview")
    readonly_fields = (
        "order",
        "move_up_down_links",
        "texture_preview",
    )
    extra = 1


@admin.register(Board)
class BoardAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    inlines = [TileInline]
    list_display = ("name",)
