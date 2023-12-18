from django.contrib import admin

from core.authentication.models import Player
from core.device.models import Device
from core.game.models import Character, Game


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
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
