from rest_framework import serializers

from app.authentication.serializers import PlayerDetailSerializer
from app.board.models import Board
from app.game.models import Character
from app.game.models import Game
from app.game.models import Participation


class JoinGameSerializer(serializers.Serializer):
    character = serializers.PrimaryKeyRelatedField(queryset=Character.objects.all())


class CreateGameSerializer(serializers.Serializer):
    max_participations = serializers.IntegerField(default=4)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    initial_balance = serializers.IntegerField(default=0)


class GameDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")
    is_lobby_full = serializers.BooleanField()

    class Meta:
        model = Game
        fields = [
            "pk",
            "status",
            "status_display",
            "max_participations",
            "owner_id",
            "board_id",
            "is_lobby_full",
        ]


class CharacterDetailSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="model.url")

    class Meta:
        model = Character
        fields = ["pk", "name", "identifier", "url"]


class ParticipationDetailSerializer(serializers.ModelSerializer):
    player = PlayerDetailSerializer()
    character = CharacterDetailSerializer()
    is_players_turn = serializers.BooleanField()
    current_tile = serializers.CharField(source="current_tile.identifier")

    class Meta:
        model = Participation
        fields = ["pk", "player", "character", "is_players_turn", "state", "current_tile", "balance"]
