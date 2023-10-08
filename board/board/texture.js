import * as THREE from "three";

const textureLoader = new THREE.TextureLoader();

export default function (url) {
  return textureLoader.load(url);
}
