from rest_framework import routers
from api.viewsets.tile import TileViewSet

router = routers.DefaultRouter()

router.register(r"tiles", TileViewSet)
