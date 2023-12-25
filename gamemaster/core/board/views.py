from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.board.registry import board_registry


class BoardExportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, identifier, format=None):
        return Response(board_registry.board_for_identifier(identifier).to_json())
