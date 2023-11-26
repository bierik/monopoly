from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.authentication.views import AuthenticationViewSet
from core.device.views import DeviceViewSet
from core.game.views import BoardExportView, GameView

router = DefaultRouter()
router.register(r"game", GameView, basename="game")
router.register(r"authentication", AuthenticationViewSet, basename="authentication")
router.register(r"device", DeviceViewSet, basename="device")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "api/board/<slug:identifier>/",
        BoardExportView.as_view(),
        name="board-export",
    ),
]
