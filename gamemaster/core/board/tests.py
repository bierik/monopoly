import pydash
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.board import BOTTOM, CORNER, LEFT, RIGHT, SIDE, TOP
from core.board.models import Board, Tile, TileTypes
from core.board.registry import UnknownBoardException, board_registry


class BoardTestCase(APITestCase):
    def test_board_gives_successor_tile(self):
        board = Board.objects.create(name="dummy")
        a = Tile.objects.create(identifier="A", type=TileTypes.CORNER)
        b = Tile.objects.create(identifier="B", type=TileTypes.CORNER)
        c = Tile.objects.create(identifier="C", type=TileTypes.CORNER)
        d = Tile.objects.create(identifier="D", type=TileTypes.CORNER)

        a.set_successor(b)
        b.set_successor(c)
        c.set_successor(d)
        d.set_successor(a)

        board.tiles.add(a, b, c, d)

        self.assertEqual(a, a.successors(0))
        self.assertEqual(b, a.successors(1))
        self.assertEqual(c, a.successors(2))
        self.assertEqual(a, a.successors(4))

    def test_retrieves_board_over_api(self):
        board = Board("A")

        board.add_node("A", type=CORNER)
        board.add_node("B", type=SIDE)
        board.add_node("C", type=CORNER)
        board.add_node("D", type=SIDE)
        board.add_node("E", type=CORNER)
        board.add_node("F", type=SIDE)
        board.add_node("G", type=CORNER)
        board.add_node("H", type=SIDE)

        board.add_edge("A", "B", direction=RIGHT)
        board.add_edge("B", "C", direction=RIGHT)
        board.add_edge("C", "D", direction=BOTTOM)
        board.add_edge("D", "E", direction=BOTTOM)
        board.add_edge("E", "F", direction=LEFT)
        board.add_edge("F", "G", direction=LEFT)
        board.add_edge("G", "H", direction=TOP)
        board.add_edge("H", "A", direction=TOP)

        board_registry.register(board, "dummy")

        response = self.client.get(reverse("board-export", kwargs={"identifier": "dummy"}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            ["A", "B", "C", "D", "E", "F", "G", "H"],
            pydash.pluck(response.json()["nodes"], "id"),
        )
