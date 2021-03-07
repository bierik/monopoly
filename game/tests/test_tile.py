from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from game.models.board import Board
from game.models.figure import Figure
from game.models.game import Game
from game.models.tile import ChancelleryTile, ChanceTile, ColoredTile, SimpleTile
from game.models.tile_group import TileGroup
from game.tests.fixtures import create_simple_game

Player = get_user_model()


class ManagesTiles(TestCase):
    def test_validates_corner_tiles(self):
        game = Game.objects.create()
        board = Board.objects.create(game=game)
        tile_group = TileGroup.objects.create(board=board)
        SimpleTile.objects.create(tile_group=tile_group, is_corner=True)
        SimpleTile.objects.create(tile_group=tile_group, is_corner=True)
        SimpleTile.objects.create(tile_group=tile_group, is_corner=True)
        SimpleTile.objects.create(tile_group=tile_group, is_corner=True)
        self.assertRaises(
            ValidationError, lambda: SimpleTile.objects.create(tile_group=tile_group, is_corner=True)
        )

    def test_orders_tiles_on_the_board(self):
        game = Game.objects.create()
        board = Board.objects.create(game=game)
        tile_group_red = TileGroup.objects.create(board=board)
        tile_group_yellow = TileGroup.objects.create(board=board)

        SimpleTile.objects.create(tile_group=tile_group_red, order=1)
        SimpleTile.objects.create(tile_group=tile_group_red, order=3)
        SimpleTile.objects.create(tile_group=tile_group_yellow, order=4)
        SimpleTile.objects.create(tile_group=tile_group_red, order=2)

        self.assertEqual(
            [1, 2, 3, 4],
            list(SimpleTile.objects.order_by("order").values_list("order", flat=True)),
        )

    def test_places_figures_on_tiles(self):
        game = create_simple_game()
        neuenburg, aarau = game["tiles"]
        horse, car = game["figures"]

        self.assertEqual(list(neuenburg.figures.all()), [horse])
        self.assertEqual(list(aarau.figures.all()), [car])

    def test_moves_figures_from_tiles(self):
        game = create_simple_game()
        neuenburg, aarau = game["tiles"]
        horse, car = game["figures"]
        cris = Player.objects.create(username="cris")
        cat = Figure.objects.create(tile=neuenburg, player=cris)

        self.assertEqual(list(neuenburg.figures.all()), [horse, cat])
        self.assertEqual(list(aarau.figures.all()), [car])

        horse.move_to(aarau)
        self.assertEqual(list(neuenburg.figures.all()), [cat])
        self.assertEqual(list(aarau.figures.all()), [car, horse])

        cat.move_to(aarau)
        self.assertEqual(list(neuenburg.figures.all()), [])
        self.assertEqual(list(aarau.figures.all()), [car, horse, cat])

        car.move_to(neuenburg)
        self.assertEqual(list(neuenburg.figures.all()), [car])
        self.assertEqual(list(aarau.figures.all()), [horse, cat])

    def test_tile_types_model(self):
        game = Game.objects.create()
        board = Board.objects.create(game=game)

        chance_tile_group = TileGroup.objects.create(board=board)
        ChanceTile.objects.create(tile_group=chance_tile_group)
        self.assertRaises(
            ValidationError, lambda: ChancelleryTile.objects.create(tile_group=chance_tile_group)
        )

        simple_tile_group = TileGroup.objects.create(board=board)
        SimpleTile.objects.create(tile_group=simple_tile_group)
        self.assertRaises(
            ValidationError, lambda: ChancelleryTile.objects.create(tile_group=simple_tile_group)
        )
        self.assertRaises(ValidationError, lambda: ColoredTile.objects.create(tile_group=simple_tile_group))

        colored_tile_group = TileGroup.objects.create(board=board)
        ColoredTile.objects.create(tile_group=colored_tile_group)
        self.assertRaises(ValidationError, lambda: SimpleTile.objects.create(tile_group=colored_tile_group))
