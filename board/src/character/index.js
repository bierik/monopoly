import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import * as THREE from "three";
import gsap from "gsap";
import * as CANNON from "cannon-es";
import { threeToCannon, ShapeType } from "three-to-cannon";

const gltfLoader = new GLTFLoader();

function pathForCharacterName(name) {
  return `/src/character/${name}.gltf`;
}

export default class Character {
  constructor(model, animations, scale = 1) {
    this.scale = scale;
    this.model = model;
    this.model.scale.set(scale, scale, scale);
    this.animations = animations;
    this.mixer = new THREE.AnimationMixer(this.model);
    this.model.updateWorldMatrix(false, true);
    this.animate("Idle");
    this.body = new CANNON.Body({
      mass: 0.001,
    });
    this.body.addShape(
      new CANNON.Box(new THREE.Vector3(0.5, 1.6, 0.5).multiplyScalar(scale)),
      new THREE.Vector3(0, 1.6, 0).multiplyScalar(scale),
    );
  }

  getSize() {
    const box = new THREE.Box3().setFromObject(this.model);
    const size = new THREE.Vector3();
    box.getSize(size);
    return size;
  }

  animate(name) {
    this.mixer.stopAllAction();
    const clip = THREE.AnimationClip.findByName(this.animations, name);
    const action = this.mixer.clipAction(clip);
    action.play();
  }

  async goTo(target, animate = false) {
    const targetPosition = target.position.clone();
    if (animate) {
      this.animate("Run");
      return new Promise((resolve) => {
        gsap.to(this.body.position, {
          x: targetPosition.x,
          y: targetPosition.y,
          z: targetPosition.z,
          ease: "none",
          duration: 8,
          onComplete: () => {
            this.animate("Idle");
            resolve();
          },
        });
      });
    } else {
      this.body.position.copy(targetPosition);
      return Promise.resolve();
    }
  }

  static async forName(name, scale = 1) {
    return new Promise((resolve, reject) => {
      gltfLoader.load(
        pathForCharacterName(name),
        (gltf) => {
          resolve(new Character(gltf.scene, gltf.animations, scale));
        },
        null,
        reject,
      );
    });
  }
}
