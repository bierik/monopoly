from django.contrib.auth import get_user_model
from game.models.game import Game
from game.models.board import Board
from game.models.tile_group import TileGroup
from game.models.tile import Tile
from game.models.figure import Figure

Player = get_user_model()


def create_simple_game():
    game = Game.objects.create()
    board = Board.objects.create(game=game)
    tile_group = TileGroup.objects.create(board=board)
    neuenburg = Tile.objects.create(title="Neuenburg Place Purry", tile_group=tile_group, order=1)
    aarau = Tile.objects.create(title="Aarau Rathausplatz", tile_group=tile_group, order=2)

    kevin = Player.objects.create(username="kevin")
    delia = Player.objects.create(username="delia")

    horse = Figure.objects.create(tile=neuenburg, player=kevin)
    car = Figure.objects.create(tile=aarau, player=delia)

    return {"tiles": (neuenburg, aarau), "figures": (horse, car)}
