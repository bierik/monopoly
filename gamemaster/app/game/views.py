from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import mixins

from app.game.models import Character
from app.game.models import Game
from app.game.models import Participation
from app.game.permissions import DeviceTokenPermission
from app.game.permissions import IsGameOwnerPermission
from app.game.permissions import IsPlayersParticipationPermission
from app.game.serializers import CharacterDetailSerializer
from app.game.serializers import CreateGameSerializer
from app.game.serializers import GameDetailSerializer
from app.game.serializers import JoinGameSerializer
from app.game.serializers import ParticipationDetailSerializer
from app.views import SerializerActionMixin


class GameView(SerializerActionMixin, GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Game.objects.all()
    serializer_action_classes = {
        "retrieve": GameDetailSerializer,
    }

    def get_permissions(self):
        if self.action in ["retrieve", "lobby"]:
            self.permission_classes = [DeviceTokenPermission | IsAuthenticated]
        elif self.action in ["start"]:
            self.permission_classes = [IsGameOwnerPermission]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    @action(methods=["POST"], detail=True)
    def join(self, request, pk=None):
        game = self.get_object()
        serializer = JoinGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participation = game.join(player=request.user, character=serializer.validated_data["character"])
        return Response(ParticipationDetailSerializer(participation).data)

    @action(methods=["GET"], detail=True)
    def lobby(self, request, pk=None):
        game = self.get_object()
        return Response(ParticipationDetailSerializer(game.participations.all(), many=True).data)

    @action(methods=["POST"], detail=True)
    def start(self, request, pk=None):
        game = self.get_object()
        game.start()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=True)
    def participation(self, request, pk=None):
        game = self.get_object()
        try:
            return Response(ParticipationDetailSerializer(game.participation_for_player(request.user)).data)
        except Participation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = CreateGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = Game.objects.create(
            owner=request.user,
            device=request.device,
            **serializer.validated_data,
        )
        return Response(data=GameDetailSerializer(Game.objects.get(pk=game.pk)).data, status=status.HTTP_201_CREATED)


class CharacterViewSet(GenericViewSet, mixins.ListModelMixin):
    queryset = Character.objects.all()
    serializer_class = CharacterDetailSerializer


class ParticipationViewSet(GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Participation.objects.all()
    serializer_class = ParticipationDetailSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsPlayersParticipationPermission],
    )
    def move(self, request, pk=None):
        self.get_object().move_random()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsPlayersParticipationPermission],
    )
    def end_turn(self, request, pk=None):
        self.get_object().end_turn()
        return Response(status=status.HTTP_204_NO_CONTENT)
