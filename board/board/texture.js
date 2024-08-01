import { TextureLoader } from "three";

const textureLoader = new TextureLoader();

export default function (url) {
  const texture = textureLoader.load(url);
  texture.generateMipmaps = false;
  return texture;
}
