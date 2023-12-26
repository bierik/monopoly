import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

export default function () {
  const gltfLoader = new GLTFLoader()
  return async function (path) {
    return new Promise((resolve, reject) => {
      gltfLoader.load(path, (gltf) => resolve(gltf), null, reject)
    })
  }
}
