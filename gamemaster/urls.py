from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.authentication.views import AuthenticationViewSet, LoginView, LogoutView
from core.board.views import BoardExportView
from core.device.views import DeviceViewSet
from core.game.views import GameView
from core.views import CSRFView

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
    path("api/login", LoginView.as_view(), name="login"),
    path("api/logout", LogoutView.as_view(), name="logout"),
    path("api/csrf", CSRFView.as_view(), name="csrf"),
]
