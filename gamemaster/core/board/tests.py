from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pydash import pluck
from rest_framework import status
from rest_framework.test import APITestCase

from core.board.models import Board, Direction, Tile, TileTypes


class BoardTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with (Path(__file__).parent / "fixtures" / "texture.webp").open("rb") as texture:
            cls.texture = SimpleUploadedFile("texture.webp", texture.read(), "image/webp")

    def test_board_gives_successor_tile(self):
        board = Board.objects.create(name="dummy")
        a = Tile.objects.create(
            identifier="A",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )
        b = Tile.objects.create(
            identifier="B",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )
        c = Tile.objects.create(
            identifier="C",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )
        d = Tile.objects.create(
            identifier="D",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )

        self.assertEqual(a, a.successor(0))
        self.assertEqual(b, a.successor(1))
        self.assertEqual(c, a.successor(2))
        self.assertEqual(a, a.successor(4))
        self.assertEqual(b, a.successor(5))
        self.assertEqual(d, c.successor(1))
        self.assertEqual(a, c.successor(2))

    def test_tile_successors(self):
        board = Board.objects.create(name="dummy")
        a = Tile.objects.create(
            identifier="A",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )
        b = Tile.objects.create(
            identifier="B",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )
        c = Tile.objects.create(
            identifier="C",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )
        d = Tile.objects.create(
            identifier="D",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )

        self.assertEqual([], list(a.successors(0)))
        self.assertEqual([b], list(a.successors(1)))
        self.assertEqual([b, c], list(a.successors(2)))
        self.assertEqual([b, c, d, a], list(a.successors(4)))
        self.assertEqual([b, c, d, a, b], list(a.successors(5)))
        self.assertEqual([b, c, d, a, b, c], list(a.successors(6)))

    def test_retrieves_board_over_api(self):
        board = Board.objects.create(name="dummy")
        corner_1 = Tile.objects.create(
            identifier="Corner 1",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.RIGHT,
            texture=self.texture,
        )
        side_1 = Tile.objects.create(
            identifier="Side 1",
            type=TileTypes.SIDE,
            board=board,
            direction=Direction.RIGHT,
            texture=self.texture,
        )
        corner_2 = Tile.objects.create(
            identifier="Corner 2",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )
        side_2 = Tile.objects.create(
            identifier="Side 2",
            type=TileTypes.SIDE,
            board=board,
            direction=Direction.BOTTOM,
            texture=self.texture,
        )
        corner_3 = Tile.objects.create(
            identifier="Corner 3",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.LEFT,
            texture=self.texture,
        )
        side_3 = Tile.objects.create(
            identifier="Side 3",
            type=TileTypes.SIDE,
            board=board,
            direction=Direction.LEFT,
            texture=self.texture,
        )
        corner_4 = Tile.objects.create(
            identifier="Corner 4",
            type=TileTypes.CORNER,
            board=board,
            direction=Direction.TOP,
            texture=self.texture,
        )
        side_4 = Tile.objects.create(
            identifier="Side 4",
            type=TileTypes.SIDE,
            board=board,
            direction=Direction.TOP,
            texture=self.texture,
        )

        board.tiles.add(corner_1, corner_2, corner_3, corner_4, side_1, side_2, side_3, side_4)

        response = self.client.get(reverse("board-detail", kwargs={"pk": board.pk}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            [
                "Corner 1",
                "Side 1",
                "Corner 2",
                "Side 2",
                "Corner 3",
                "Side 3",
                "Corner 4",
                "Side 4",
            ],
            pluck(response.json()["tiles"], "identifier"),
        )
        self.assertEqual(
            [
                "RIGHT",
                "RIGHT",
                "BOTTOM",
                "BOTTOM",
                "LEFT",
                "LEFT",
                "TOP",
                "TOP",
            ],
            pluck(response.json()["tiles"], "direction"),
        )
