import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const gltfLoader = new GLTFLoader();

export function loadGLTF(path) {
  return new Promise((resolve, reject) => {
    gltfLoader.load(path, (model) => resolve(model), null, reject);
  });
}
