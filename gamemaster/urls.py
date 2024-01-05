from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.authentication.views import AuthenticationViewSet, LoginView, LogoutView
from core.board.views import BoardViewSet
from core.device.views import DeviceViewSet
from core.game.views import CharacterViewSet, GameView
from core.views import CSRFView

router = DefaultRouter()
router.register(r"game", GameView, basename="game")
router.register(r"authentication", AuthenticationViewSet, basename="authentication")
router.register(r"device", DeviceViewSet, basename="device")
router.register(r"character", CharacterViewSet, basename="character")
router.register(r"board", BoardViewSet, basename="board")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/csrf/", CSRFView.as_view(), name="csrf"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
