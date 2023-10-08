import * as THREE from "three";

import { textureForName } from "@/textures";

const ATTACH_TO = {
  RIGHT: "right",
  BOTTOM: "bottom",
  LEFT: "left",
  TOP: "top",
};

const BOARD_STRUCTURE = [
  // [0, null], initial value
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [1, ATTACH_TO.RIGHT, "wasserwerk"],
  [0, ATTACH_TO.RIGHT, "police"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [1, ATTACH_TO.BOTTOM, "luzern"],
  [0, ATTACH_TO.BOTTOM, "start"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [1, ATTACH_TO.LEFT, "elektrizitaetswerk"],
  [0, ATTACH_TO.LEFT, "jail"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
  [1, ATTACH_TO.TOP, "basel_steinenvorstadt"],
];

class Tile extends THREE.Mesh {
  constructor(...params) {
    super(...params);
    this.rotateX(-Math.PI / 2);
  }

  highlight() {
    this.material.color = new THREE.Color(0xff0000);
  }

  placeNext(nextTo, attachTo) {
    this.nextTo = nextTo;
    nextTo.parent = this;
    switch (attachTo) {
      case ATTACH_TO.BOTTOM:
        nextTo.rotateZ(Math.PI / 2);
        nextTo.position.x = this.position.x;
        nextTo.position.z =
          this.position.z +
          this.geometry.parameters.width / 2 +
          nextTo.geometry.parameters.width / 2;
        break;
      case ATTACH_TO.TOP:
        nextTo.rotateZ(Math.PI / 2);
        nextTo.position.y = this.position.y;
        nextTo.position.z =
          this.position.z -
          this.geometry.parameters.width / 2 -
          nextTo.geometry.parameters.width / 2;
        break;
      case ATTACH_TO.RIGHT:
        nextTo.position.x =
          this.position.x +
          this.geometry.parameters.width / 2 +
          nextTo.geometry.parameters.width / 2;
        break;
      case ATTACH_TO.LEFT:
        nextTo.position.z = this.position.z;
        nextTo.position.x =
          this.position.x -
          this.geometry.parameters.width / 2 -
          nextTo.geometry.parameters.width / 2;
        break;
    }
  }
}

class CornerTile extends Tile {
  constructor(...params) {
    super(...params);
    this.geometry = new THREE.PlaneGeometry(12, 12);
    this.material = new THREE.MeshStandardMaterial();
  }
}

class SideTile extends Tile {
  constructor(...params) {
    super(...params);
    this.geometry = new THREE.PlaneGeometry(6, 12);
    this.material = new THREE.MeshStandardMaterial();
  }
}

const TILE_TYPE = {
  0: CornerTile,
  1: SideTile,
};

const board = new THREE.Object3D();

const initialTile = new CornerTile();
initialTile.material.map = textureForName("parking");
initialTile.name = "parking";
board.add(initialTile);

BOARD_STRUCTURE.reduce((prev, current) => {
  const [tileType, attachTo, textureName] = current;
  const tile = new TILE_TYPE[tileType]();
  if (textureName) {
    tile.material.map = textureForName(textureName);
    tile.name = textureName;
  }
  prev.placeNext(tile, attachTo);
  board.add(tile);
  return tile;
}, initialTile);

export default board;
