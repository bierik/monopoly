from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from core.board.registry import board_registry
from core.game.models import Game
from core.game.serializers import (
    CreateGameSerializer,
    GameDetailSerializer,
    JoinGameSerializer,
)


class GameView(GenericViewSet):
    queryset = Game.objects.all()

    @action(methods=["POST"], detail=True)
    def join(self, request, pk=None):
        game = self.get_object()
        serializer = JoinGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game.join(player=request.user, character=serializer.validated_data["character"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        serializer = CreateGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = Game.objects.create(owner=request.user)
        game.join(player=request.user, character=serializer.validated_data["character"])
        return Response(
            data=GameDetailSerializer(game).data, status=status.HTTP_201_CREATED
        )


class BoardExportView(APIView):
    def get(self, request, identifier, format=None):
        return Response(board_registry.board_for_identifier(identifier).to_json())
