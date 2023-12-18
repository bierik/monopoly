from django.contrib import admin

from core.authentication.models import Player
from core.game.models import Character


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    pass
