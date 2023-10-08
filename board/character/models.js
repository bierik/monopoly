import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const gltfLoader = new GLTFLoader();
export default function (path) {
  return new Promise((resolve, reject) => {
    gltfLoader.load(path, (gltf) => resolve(gltf), null, reject);
  });
}
