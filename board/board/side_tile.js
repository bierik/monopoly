import Tile from "@/board/tile";
import { BoxGeometry } from "three";

const geometry = new BoxGeometry(6 * 0.6, 0.5, 6);

export default class SideTile extends Tile {
  constructor() {
    super();
    this.geometry = geometry;
  }
}
