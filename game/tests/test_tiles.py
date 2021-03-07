from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from game.models.tile import Tile
from game.models.figure import Figure
from game.tests.fixtures import create_simple_game
from game.models.game import Game
from game.models.board import Board
from game.models.tile_group import TileGroup


Player = get_user_model()


class ManagesTiles(TestCase):
    def test_validates_corner_tiles(self):
        game = Game.objects.create()
        board = Board.objects.create(game=game)
        tile_group = TileGroup.objects.create(board=board)
        Tile.objects.create(tile_group=tile_group, is_corner=True)
        Tile.objects.create(tile_group=tile_group, is_corner=True)
        Tile.objects.create(tile_group=tile_group, is_corner=True)
        Tile.objects.create(tile_group=tile_group, is_corner=True)
        self.assertRaises(ValidationError, lambda: Tile.objects.create(tile_group=tile_group, is_corner=True))

    def test_orders_tiles_on_the_board(self):
        game = create_simple_game()
        neuenburg, aarau = game["tiles"]

        self.assertEqual(
            [neuenburg.title, aarau.title],
            list(Tile.get_ordering_queryset(Tile).values_list("title", flat=True)),
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
