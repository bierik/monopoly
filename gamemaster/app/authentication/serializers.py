from rest_framework import serializers

from app.authentication.models import Player


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class PlayerDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")

    class Meta:
        model = Player
        fields = ["pk", "username", "first_name", "last_name", "full_name"]
