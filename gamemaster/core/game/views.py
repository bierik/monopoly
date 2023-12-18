from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from core.game.models import Game
from core.game.serializers import (
    CreateGameSerializer,
    GameDetailSerializer,
    JoinGameSerializer,
)
from core.mqtt_client import mqtt_client
from core.views import SerializerActionMixin


class GameView(SerializerActionMixin, GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Game.objects.all()
    serializer_action_classes = {
        "retrieve": GameDetailSerializer,
    }

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
        game = Game.objects.create(
            owner=request.user,
            max_participations=serializer.validated_data["max_participations"],
        )
        game.join(player=request.user, character=serializer.validated_data["character"])
        return Response(
            data=GameDetailSerializer(game).data, status=status.HTTP_201_CREATED
        )
