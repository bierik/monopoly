import Tile from "@/board/tile";
import { PlaneGeometry, MeshStandardMaterial } from "three";

export default class CornerTile extends Tile {
  constructor(...params) {
    super(...params);
    this.geometry = new PlaneGeometry(12, 12);
    this.material = new MeshStandardMaterial();
  }
}
