import { TextureLoader } from "three";

const textureLoader = new TextureLoader();

export default function (url) {
  return textureLoader.load(url);
}
