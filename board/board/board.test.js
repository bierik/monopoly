import { expect, test } from "vitest";
import { Scene } from "three";
import Board from "@/board";

test("creates path on board", () => {
  const scene = new Scene();
  const board = new Board(
    {
      tiles: [
        { identifier: "1", type: "CORNER", direction: "RIGHT", texture: "" },
        { identifier: "2", type: "CORNER", direction: "RIGHT", texture: "" },
        { identifier: "3", type: "CORNER", direction: "RIGHT", texture: "" },
        { identifier: "4", type: "CORNER", direction: "RIGHT", texture: "" },
        { identifier: "5", type: "CORNER", direction: "RIGHT", texture: "" },
        { identifier: "6", type: "CORNER", direction: "RIGHT", texture: "" },
        { identifier: "7", type: "CORNER", direction: "RIGHT", texture: "" },
        { identifier: "8", type: "CORNER", direction: "RIGHT", texture: "" },
      ],
    },
    scene,
  );
  expect(Array.from(board.buildPath("7", "1"))).toEqual(["8"]);
  expect(Array.from(board.buildPath("8", "1"))).toEqual([]);
  expect(Array.from(board.buildPath("1", "4"))).toEqual(["2", "3"]);
});
