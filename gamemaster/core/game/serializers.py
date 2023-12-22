from core.authentication.serializers import PlayerDetailSerializer
from core.game.models import Character, Game, Participation
from rest_framework import serializers


class JoinGameSerializer(serializers.Serializer):
    character = serializers.PrimaryKeyRelatedField(queryset=Character.objects.all())


class CreateGameSerializer(serializers.Serializer):
    max_participations = serializers.IntegerField(default=4)


class GameDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")

    class Meta:
        model = Game
        fields = ["pk", "status", "status_display"]


class CharacterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ["pk", "name", "identifier"]


class ParticipationLobbySerializer(serializers.ModelSerializer):
    player = PlayerDetailSerializer()
    character = CharacterDetailSerializer()

    class Meta:
        model = Participation
        fields = ["pk", "player", "character"]
