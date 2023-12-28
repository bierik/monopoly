import pydash
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.board import BOTTOM, CORNER, LEFT, RIGHT, SIDE, TOP
from core.board.board import Board
from core.board.registry import UnknownBoardException, board_registry


class BoardTestCase(APITestCase):
    def test_raises_an_error_when_the_structure_does_not_exist(self):
        with self.assertRaises(UnknownBoardException):
            board_registry.board_for_identifier("unknown")

    def test_gives_board_for_identifier(self):
        self.assertIsNotNone(board_registry.board_for_identifier("monopoly"))

    def test_board_gives_successor_tile(self):
        board = Board("A")

        board.add_node("A")
        board.add_node("B")
        board.add_node("C")
        board.add_node("D")

        board.add_edge("A", "B")
        board.add_edge("B", "C")
        board.add_edge("C", "D")
        board.add_edge("D", "A")

        self.assertEqual("B", board.successor_of("A"))
        self.assertEqual("C", board.successor_of("A", 2))
        self.assertEqual("A", board.successor_of("A", 4))

    def test_serialize_board(self):
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

        json_data = board.to_json()
        self.assertEqual(
            ["A", "B", "C", "D", "E", "F", "G", "H"],
            pydash.pluck(json_data["nodes"], "id"),
        )

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
