from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from core.authentication.serializers import (
    LoginRequestSerializer,
    PlayerDetailSerializer,
)
from core.game.models import Game
from core.game.serializers import GameDetailSerializer


class AuthenticationViewSet(GenericViewSet):
    @action(methods=["GET"], detail=False)
    def games(self, request):
        return Response(GameDetailSerializer(Game.objects.owned(request.user), many=True).data)

    @action(methods=["GET"], detail=False)
    def me(self, request):
        return Response(PlayerDetailSerializer(request.user).data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, **kwrags):
        serializer = LoginRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise AuthenticationFailed
        user = authenticate(**serializer.validated_data)
        if not user:
            raise AuthenticationFailed
        login(request, user)
        return Response(PlayerDetailSerializer(user).data)


class LogoutView(APIView):
    def post(self, request, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
