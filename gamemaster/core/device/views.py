from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.device.models import Device
from core.device.serializers import DeviceDetailSerializer


class DeviceViewSet(GenericViewSet):
    @action(methods=["POST"], detail=False, permission_classes=[AllowAny])
    def register(self, request):
        if not request.device:
            device = Device.register(request.META.get("HTTP_USER_AGENT", ""))
            return Response(DeviceDetailSerializer(device).data, status=status.HTTP_201_CREATED)
        return Response(DeviceDetailSerializer(request.device).data, status=status.HTTP_200_OK)
