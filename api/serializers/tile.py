from rest_framework import serializers
from game.models.tile import SimpleTile
from game.models.tile import ColoredTile
from game.models.tile import ChanceTile
from game.models.tile import ChancelleryTile
from rest_polymorphic.serializers import PolymorphicSerializer


class SimpleTileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleTile
        fields = ("id", "title", "subtitle", "is_corner")


class ColoredTileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColoredTile
        fields = ("id", "title", "subtitle", "color", "is_corner")


class ChanceTileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChanceTile
        fields = ("id", "title", "is_corner")


class ChancelleryTileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChancelleryTile
        fields = ("id", "title", "is_corner")


class ProjectPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        SimpleTile: SimpleTileSerializer,
        ColoredTile: ColoredTileSerializer,
        ChanceTile: ChanceTileSerializer,
        ChancelleryTile: ChancelleryTileSerializer,
    }
