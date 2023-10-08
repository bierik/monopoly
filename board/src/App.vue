<template>
  <canvas ref="canvas" />
</template>
<script setup>
import * as THREE from "three";
import { onMounted, watch, ref } from "vue";
import { useWindowSize } from "@vueuse/core";
import board from "@/meshes/board";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import Character from "@/character";
import * as CANNON from "cannon-es";
import CannonDebugger from "cannon-es-debugger";
import { threeToCannon, ShapeType } from "three-to-cannon";

const canvas = ref(null);
const { width: windowWidth, height: windowHeight } = useWindowSize();
const aspect = windowWidth.value / windowHeight.value;

const mixers = [];

onMounted(async () => {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xeaeaea);

  const camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
  camera.position.set(10, 10, 80);

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    canvas: canvas.value,
  });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setSize(windowWidth.value, windowHeight.value);

  watch([windowWidth, windowHeight], ([newWidth, newHeight]) => {
    camera.aspect = newWidth / newHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(newWidth, newHeight);
  });

  const light = new THREE.AmbientLight(0xffffff, Math.PI);
  scene.add(light);

  const controls = new OrbitControls(camera, canvas.value);
  controls.update();
  scene.add(board);

  const parking = board.getObjectByName("parking");
  const jail = board.getObjectByName("jail");
  const start = board.getObjectByName("start");

  const casualMale = await Character.forName("casual_male", 2);
  mixers.push(casualMale.mixer);
  scene.add(casualMale.model);
  await casualMale.goTo(jail);

  const casualMale2 = await Character.forName("casual_male", 2);
  mixers.push(casualMale2.mixer);
  scene.add(casualMale2.model);

  const world = new CANNON.World({
    gravity: new CANNON.Vec3(0, -9.81, 0),
  });

  const aabb = new THREE.Box3();
  aabb.setFromObject(board);
  const bla = new THREE.Vector3();
  aabb.getSize(bla);

  const ground = new CANNON.Body({
    shape: new CANNON.Box(new CANNON.Vec3(bla.x / 2, bla.z / 2, 1)),
    type: CANNON.Body.STATIC,
    position: new CANNON.Vec3(
      bla.x / 2 - parking.geometry.parameters.width / 2,
      -1,
      bla.z / 2 - parking.geometry.parameters.height / 2,
    ),
  });
  ground.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
  world.addBody(ground);
  world.addBody(casualMale.body);
  world.addBody(casualMale2.body);

  const timeStep = 1 / 60;

  const cannonDebugger = new CannonDebugger(scene, world);

  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    world.step(timeStep);
    cannonDebugger.update();
    const delta = clock.getDelta();
    mixers.forEach((mixer) => {
      mixer.update(delta);
    });

    casualMale.model.position.copy(casualMale.body.position);
    casualMale.model.quaternion.copy(casualMale.body.quaternion);
    casualMale2.model.position.copy(casualMale2.body.position);
    casualMale2.model.quaternion.copy(casualMale2.body.quaternion);

    renderer.render(scene, camera);
  });
  await casualMale2.goTo(jail, true);
  await casualMale2.goTo(start, true);
});
</script>
