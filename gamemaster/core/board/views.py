from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet, mixins

from core.board.models import Board
from core.board.serializers import BoardDetailSerializer, BoardListSerializer
from core.views import SerializerActionMixin


class BoardViewSet(
    SerializerActionMixin,
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    permission_classes = [AllowAny]
    queryset = Board.objects.all()
    serializer_action_classes = {
        "retrieve": BoardDetailSerializer,
        "list": BoardListSerializer,
    }
