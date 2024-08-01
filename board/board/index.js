import CornerTile from "@/board/corner_tile";
import SideTile from "@/board/side_tile";
import Character from "@/character";
import { first, drop, findIndex, find, size } from "lodash-es";
import loadTexture from "@/board/texture";
import { Object3D } from "three";
import { EntityManager } from "yuka";

const TILE_TYPE = {
  CORNER: CornerTile,
  SIDE: SideTile,
};

export default class Board {
  constructor(structure, scene) {
    this.model = new Object3D();
    this.characterManager = new EntityManager();
    this.scene = scene;
    this.structure = structure;
    this.buildBoard();
  }

  buildBoard() {
    const tiles = this.structure.tiles;
    const rootTile = this.createTile(first(tiles));
    drop(tiles, 1).reduce((current, successor) => {
      const successorTile = this.createTile(successor);
      current.placeNextTo(successorTile, successor.direction);
      return successorTile;
    }, rootTile);
  }

  *buildPath(from, to) {
    const start = findIndex(this.structure.tiles, { identifier: from });
    const end = findIndex(this.structure.tiles, { identifier: to });
    const totalTiles = size(this.structure.tiles);
    let current = (start + 1) % totalTiles;
    while (current !== end) {
      yield this.structure.tiles[current].identifier;
      current = (current + 1) % totalTiles;
    }
  }

  createTile({ type, texture, identifier }) {
    const tile = new TILE_TYPE[type]();
    tile.material.map = loadTexture(texture);
    tile.name = identifier;
    this.model.add(tile);
    return tile;
  }

  tileForName(tile) {
    return this.model.getObjectByName(tile);
  }

  update(delta) {
    this.characterManager.update(delta);
  }

  async addCharacter(args) {
    const character = await Character.fromModel({
      board: this,
      ...args,
    });
    this.scene.add(character.model);
    this.characterManager.add(character);
    return character;
  }

  moveCharacter(identifier, tile) {
    const character = find(this.characterManager.entities, { identifier });
    character.goTo(tile);
  }
}
