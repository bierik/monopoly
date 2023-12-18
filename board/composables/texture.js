import * as THREE from 'three'

const textureLoader = new THREE.TextureLoader()

function pathForTextureName(name) {
  return `/textures/${name}.png`
}

export default function (name) {
  const textureURL = new URL(pathForTextureName(name), import.meta.url).href
  return textureLoader.load(textureURL)
}
