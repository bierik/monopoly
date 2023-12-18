from rest_framework import serializers

from core.game.models import Character, Game


class JoinGameSerializer(serializers.Serializer):
    character = serializers.PrimaryKeyRelatedField(queryset=Character.objects.all())
    max_participations = serializers.IntegerField(default=4)


class CreateGameSerializer(JoinGameSerializer):
    pass


class GameDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")

    class Meta:
        model = Game
        fields = ["pk", "status", "status_display"]
