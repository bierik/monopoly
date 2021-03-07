from rest_framework import viewsets
from rest_framework.viewsets import mixins
from game.models.tile import Tile
from api.serializers.tile import ProjectPolymorphicSerializer


class TileViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Tile.objects.order_by("order")
    serializer_class = ProjectPolymorphicSerializer
