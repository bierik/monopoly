import * as THREE from "three";
import Tile from "@/board/tile";

export default class CornerTile extends Tile {
  constructor(...params) {
    super(...params);
    this.geometry = new THREE.PlaneGeometry(12, 12);
    this.material = new THREE.MeshStandardMaterial();
  }
}
