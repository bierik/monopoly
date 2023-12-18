import * as THREE from 'three'
import { textureForName } from '@/textures'
import CornerTile from '@/board/corner_tile'
import SideTile from '@/board/side_tile'
import * as YUKA from 'yuka'
import Character from '@/character'
import Graph from '@/board/graph'

const TILE_TYPE = {
  0: CornerTile,
  1: SideTile,
}

export default class Board {
  constructor(graph, scene) {
    this.model = new THREE.Object3D()
    this.characterManager = new YUKA.EntityManager()
    this.graph = graph
    this.scene = scene
    this.createdTiles = {}
    this.buildBoard()
  }

  buildBoard() {
    this.graph.traverse(({ node, successor, edge }) => {
      const nodeTile = this.createTile(node.id, node.type)
      const successorTile = this.createTile(successor.id, successor.type)
      nodeTile.placeNextTo(successorTile, edge.direction)
    })
  }

  createTile(id, type) {
    if (id in this.createdTiles) {
      return this.createdTiles[id]
    }
    const tile = new TILE_TYPE[type]()
    tile.material.map = textureForName(id)
    tile.name = id
    this.model.add(tile)
    this.createdTiles[id] = tile
    return tile
  }

  static fromNodeLinkGraph(nodeLinkGraph, scene) {
    const graph = Graph.fromNodeLinkGraph(nodeLinkGraph)
    return new Board(graph, scene)
  }

  tileForName(tile) {
    return this.model.getObjectByName(tile)
  }

  update(delta) {
    this.characterManager.update(delta)
  }

  async addCharacter({ name, target = this.graph.rootNode, scale = 1 }) {
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
