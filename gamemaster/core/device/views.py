from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.device.models import Device


class DeviceViewSet(GenericViewSet):
    @action(methods=["POST"], detail=False)
    def register(self, request):
        Device.register(request.META.get("HTTP_USER_AGENT", ""))
        return Response(status=status.HTTP_204_NO_CONTENT)
