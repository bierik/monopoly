import * as THREE from "three";
import CornerTile from "@/board/corner_tile";
import SideTile from "@/board/side_tile";
import * as YUKA from "yuka";
import Character from "@/character";
import { first, drop, findIndex, map, find } from "lodash-es";
import loadTexture from "@/board/texture";

const TILE_TYPE = {
  CORNER: CornerTile,
  SIDE: SideTile,
};

export default class Board {
  constructor(structure, scene) {
    this.model = new THREE.Object3D();
    this.characterManager = new YUKA.EntityManager();
    this.scene = scene;
    this.structure = structure;
    this.buildBoard();
  }

  buildBoard() {
    const tiles = this.structure.tiles;
    const rootTile = this.createTile(first(tiles));
    drop(tiles, 1).reduce((bla, successor) => {
      const successorTile = this.createTile(successor);
      bla.placeNextTo(successorTile, successor.direction);
      return successorTile;
    }, rootTile);
  }

  buildPath(from, to) {
    const startTile = findIndex(this.structure.tiles, { identifier: from });
    const endTile = findIndex(this.structure.tiles, { identifier: to });
    return map(this.structure.tiles.slice(startTile, endTile), "identifier");
  }

  createTile(bla) {
    const tile = new TILE_TYPE[bla.type]();
    tile.material.map = loadTexture(bla.texture);
    tile.name = bla.identifier;
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
