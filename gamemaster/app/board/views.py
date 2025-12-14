from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import mixins

from app.board.models import Board
from app.board.serializers import BoardDetailSerializer
from app.board.serializers import BoardListSerializer
from app.views import SerializerActionMixin


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
