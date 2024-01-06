import * as THREE from 'three'
import CornerTile from '@/board/corner_tile'
import SideTile from '@/board/side_tile'
import * as YUKA from 'yuka'
import Character from '@/character'
import first from 'lodash/first'
import drop from 'lodash/drop'
import loadTexture from '@/board/texture'
import findIndex from 'lodash/findIndex'
import map from 'lodash/map'

const TILE_TYPE = {
  CORNER: CornerTile,
  SIDE: SideTile,
}

export default class Board {
  constructor(structure, scene) {
    this.model = new THREE.Object3D()
    this.characterManager = new YUKA.EntityManager()
    this.scene = scene
    this.structure = structure
    this.buildBoard()
  }

  buildBoard() {
    const tiles = this.structure.tiles
    const rootTile = this.createTile(first(tiles))
    drop(tiles, 1).reduce((bla, successor) => {
      const successorTile = this.createTile(successor)
      bla.placeNextTo(successorTile, successor.direction)
      return successorTile
    }, rootTile)
  }

  buildPath(from, to) {
    const startTile = findIndex(this.structure.tiles, { identifier: from })
    const endTile = findIndex(this.structure.tiles, { identifier: to })
    return map(this.structure.tiles.slice(startTile, endTile + 1), 'identifier')
  }

  createTile(bla) {
    const tile = new TILE_TYPE[bla.type]()
    tile.material.map = loadTexture(bla.texture)
    tile.name = bla.identifier
    this.model.add(tile)
    return tile
  }

  tileForName(tile) {
    return this.model.getObjectByName(tile)
  }

  update(delta) {
    this.characterManager.update(delta)
  }

  async addCharacter({ model, target, scale = 1 }) {
    const character = await Character.fromModel({
      model,
      board: this,
      target,
      scale,
    })
    this.scene.add(character.model)
    this.characterManager.add(character)
    return character
  }
}
