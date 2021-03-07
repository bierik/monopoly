from game.models.tile import SimpleTile
from game.models.tile import ColoredTile
from game.models.tile import ChanceTile
from game.models.tile import ChancelleryTile
from game.models.tile_group import TileGroup
from game.models.board import Board
from game.models.game import Game
from api.tests import ApiTestCase
from pluck import pluck


class TestTileSerializer(ApiTestCase):
    def test_tile_list(self):
        game = Game.objects.create()
        board = Board.objects.create(game=game)
        simple_tile_group = TileGroup.objects.create(board=board)
        colored_tile_group = TileGroup.objects.create(board=board)
        chance_tile_group = TileGroup.objects.create(board=board)
        chancellery_tile_group = TileGroup.objects.create(board=board)
        SimpleTile.objects.create(tile_group=simple_tile_group)
        ColoredTile.objects.create(tile_group=colored_tile_group)
        ChanceTile.objects.create(tile_group=chance_tile_group)
        ChancelleryTile.objects.create(tile_group=chancellery_tile_group)

        response = self.client.get("/api/tiles/")
        self.assertEqual(
            pluck(response.json(), "resourcetype"),
            ["SimpleTile", "ColoredTile", "ChanceTile", "ChancelleryTile"],
        )
