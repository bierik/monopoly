from rest_framework import serializers

from core.authentication.serializers import PlayerDetailSerializer
from core.game.models import Character, Game, Participation


class JoinGameSerializer(serializers.Serializer):
    character = serializers.PrimaryKeyRelatedField(queryset=Character.objects.all())


class CreateGameSerializer(serializers.Serializer):
    max_participations = serializers.IntegerField(default=4)


class GameDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")

    class Meta:
        model = Game
        fields = ["pk", "status", "status_display", "max_participations", "owner_id", "board_id"]


class CharacterDetailSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="model.url")

    class Meta:
        model = Character
        fields = ["pk", "name", "identifier", "url"]


class ParticipationDetailSerializer(serializers.ModelSerializer):
    player = PlayerDetailSerializer()
    character = CharacterDetailSerializer()

    class Meta:
        model = Participation
        fields = ["pk", "player", "character"]
