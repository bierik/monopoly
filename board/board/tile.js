import * as THREE from "three";
import * as YUKA from "yuka";

const ATTACH_TO = {
  RIGHT: "RIGHT",
  BOTTOM: "BOTTOM",
  LEFT: "LEFT",
  TOP: "TOP",
};

export default class Tile extends THREE.Mesh {
  constructor(...params) {
    super(...params);
    this.rotateX(-Math.PI / 2);
    this.occupiedSpots = {};
  }

  toYUKAVector() {
    return new YUKA.Vector3(this.position.x, this.position.y, this.position.z);
  }

  isEqual(to) {
    return this.uuid === to.uuid;
  }

  getAvailableSpots() {
    const { width, height } = this.geometry.parameters;
    const subtileWidth = this.rotation.z === 0 ? width / 4 : height / 4;
    const subtileHeight = this.rotation.z === 0 ? height / 4 : width / 4;
    return [
      this.position
        .clone()
        .add(new THREE.Vector3(subtileWidth, 0, subtileHeight).divideScalar(2)),
      this.position
        .clone()
        .add(
          new THREE.Vector3(-subtileWidth, 0, +subtileHeight).divideScalar(2),
        ),
      this.position
        .clone()
        .add(
          new THREE.Vector3(+subtileWidth, 0, -subtileHeight).divideScalar(2),
        ),
      this.position
        .clone()
        .add(
          new THREE.Vector3(-subtileWidth, 0, -subtileHeight).divideScalar(2),
        ),
    ];
  }

  occupySpot(character) {
    const freeSpot = this.getFreeSpot();
    this.occupiedSpots[character.uuid] = freeSpot;
    return freeSpot;
  }

  freeSpot(character) {
    delete this.occupiedSpots[character.uuid];
  }

  getFreeSpot() {
    return this.getAvailableSpots()[Object.keys(this.occupiedSpots).length];
  }

  getSpotForCharacter(character) {
    return this.occupiedSpots[character.uuid];
  }

  placeNextTo(nextTo, attachTo) {
    switch (attachTo) {
      case ATTACH_TO.BOTTOM:
        nextTo.rotateZ(Math.PI / 2);
        nextTo.position.x = this.position.x;
        nextTo.position.z =
          this.position.z +
          this.geometry.parameters.width / 2 +
          nextTo.geometry.parameters.width / 2;
        break;
      case ATTACH_TO.TOP:
        nextTo.rotateZ(Math.PI / 2);
        nextTo.position.x = this.position.x;
        nextTo.position.z =
          this.position.z -
          this.geometry.parameters.width / 2 -
          nextTo.geometry.parameters.width / 2;
        break;
      case ATTACH_TO.RIGHT:
        nextTo.position.z = this.position.z;
        nextTo.position.x =
          this.position.x +
          this.geometry.parameters.width / 2 +
          nextTo.geometry.parameters.width / 2;
        break;
      case ATTACH_TO.LEFT:
        nextTo.position.z = this.position.z;
        nextTo.position.x =
          this.position.x -
          this.geometry.parameters.width / 2 -
          nextTo.geometry.parameters.width / 2;
        break;
    }
  }
}
