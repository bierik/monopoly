import Tile from "@/board/tile";
import { PlaneGeometry, MeshStandardMaterial } from "three";

export default class SideTile extends Tile {
  constructor(...params) {
    super(...params);
    this.geometry = new PlaneGeometry(6, 12);
    this.material = new MeshStandardMaterial();
  }
}
