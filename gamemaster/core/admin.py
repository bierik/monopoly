from core.authentication.models import Player
from django.contrib import admin


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass
