import * as THREE from "three";
import Tile from "@/board/tile";

export default class SideTile extends Tile {
  constructor(...params) {
    super(...params);
    this.geometry = new THREE.PlaneGeometry(6, 12);
    this.material = new THREE.MeshStandardMaterial();
  }
}
