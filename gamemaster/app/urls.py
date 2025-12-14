from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.routers import SimpleRouter

from app.authentication.views import AuthenticationViewSet
from app.authentication.views import LoginView
from app.authentication.views import LogoutView
from app.board.views import BoardViewSet
from app.device.views import DeviceViewSet
from app.game.views import CharacterViewSet
from app.game.views import GameView
from app.game.views import ParticipationViewSet
from app.views import CSRFView


router = SimpleRouter(trailing_slash=False)
router.register("game", GameView, basename="game")
router.register("authentication", AuthenticationViewSet, basename="authentication")
router.register("device", DeviceViewSet, basename="device")
router.register("character", CharacterViewSet, basename="character")
router.register("board", BoardViewSet, basename="board")
router.register("participation", ParticipationViewSet, basename="participation")

urlpatterns = [
    path("", RedirectView.as_view(url="api/docs", permanent=False)),
    path("api/", RedirectView.as_view(url="docs", permanent=False)),
    path("api/v1/login", LoginView.as_view(), name="login"),
    path("api/v1/logout", LogoutView.as_view(), name="logout"),
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/", include(router.urls)),
    path("api/v1/csrf", CSRFView.as_view(), name="csrf"),
    path("admin/", admin.site.urls),
]
