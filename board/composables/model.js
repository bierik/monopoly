import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const gltfLoader = new GLTFLoader()

function pathForName(name) {
  return `/models/${name}.gltf`
}

export default async function (name) {
  return new Promise((resolve, reject) => {
    gltfLoader.load(pathForName(name), (gltf) => resolve(gltf), null, reject)
  })
}
