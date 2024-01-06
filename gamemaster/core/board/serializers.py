from rest_framework import serializers

from core.board.models import Board, Tile


class TileSerializer(serializers.ModelSerializer):
    texture = serializers.CharField(source="texture.url")

    class Meta:
        model = Tile
        fields = ["identifier", "type", "direction", "texture"]


class BoardDetailSerializer(serializers.ModelSerializer):
    tiles = TileSerializer(many=True)

    class Meta:
        model = Board
        fields = ["pk", "name", "tiles"]


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ["pk", "name"]
