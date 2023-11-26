from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.game.models import Game
from core.game.serializers import GameDetailSerializer


class AuthenticationViewSet(GenericViewSet):
    @action(methods=["GET"], detail=False)
    def games(self, request):
        return Response(
            GameDetailSerializer(Game.objects.owned(request.user), many=True).data
        )
