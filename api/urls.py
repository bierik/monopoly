from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.game.views import GameView

router = DefaultRouter()
router.register(r"game", GameView, basename="game")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
