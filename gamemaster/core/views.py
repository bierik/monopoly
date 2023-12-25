from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class CSRFView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        get_token(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SerializerActionMixin:
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
