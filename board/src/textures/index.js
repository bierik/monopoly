import * as THREE from 'three'

const textureLoader = new THREE.TextureLoader()

function pathForTextureName (name) {
  return `/src/textures/${name}.png`
}

export function textureForName (name) {
  const textureURL = new URL(pathForTextureName(name), import.meta.url).href
  return textureLoader.load(textureURL)
}
