from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet, mixins

from core.board.models import Board
from core.board.serializers import BoardSerializer


class BoardViewSet(GenericViewSet, mixins.RetrieveModelMixin):
    permission_classes = [AllowAny]
    serializer_class = BoardSerializer
    queryset = Board.objects.all()
