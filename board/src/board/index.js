import * as THREE from 'three'
import { textureForName } from '@/textures'
import CornerTile from '@/board/corner_tile'
import SideTile from '@/board/side_tile'
import BOARD_STRUCTURE from '@/board/board_strucutre'
import * as YUKA from 'yuka'
import Character from '@/character'
import first from 'lodash/first'
import drop from 'lodash/drop'

const TILE_TYPE = {
  0: CornerTile,
  1: SideTile,
}

export default class Board {
  constructor(scene) {
    this.model = new THREE.Object3D()

    const [tileType, , texture] = first(BOARD_STRUCTURE)
    const initialTile = new TILE_TYPE[tileType]()
    initialTile.material.map = textureForName(texture)
    initialTile.name = texture
    this.model.add(initialTile)
    this.characterManager = new YUKA.EntityManager()
    this.scene = scene

    const lastTile = drop(BOARD_STRUCTURE, 1).reduce((prev, current) => {
      const [tileType, attachTo, textureName] = current
      const tile = new TILE_TYPE[tileType]()
      if (textureName) {
        tile.material.map = textureForName(textureName)
        tile.name = textureName
      }
      prev.placeNextTo(tile, attachTo)
      this.model.add(tile)
      return tile
    }, initialTile)
    initialTile.parentTile = lastTile
  }

  tileForName(tile) {
    return this.model.getObjectByName(tile)
  }

  update(delta) {
    this.characterManager.update(delta)
  }

  async addCharacter({ name, target = 'start', scale = 1 }) {
    const character = await Character.forName({
      name,
      board: this,
      target,
      scale,
    })
    this.scene.add(character.model)
    this.characterManager.add(character)
    return character
  }
}
