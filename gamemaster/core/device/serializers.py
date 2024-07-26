from rest_framework import serializers

from core.device.models import Device


class DeviceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["pk", "token", "user_agent"]
