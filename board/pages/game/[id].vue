<template>
  <canvas ref="canvas" />
</template>
<script setup>
import * as THREE from "three";
import Board from "@/board";
import { useWindowSize } from "@vueuse/core";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import * as YUKA from "yuka";

const canvas = ref(null);
const { width: windowWidth, height: windowHeight } = useWindowSize();
const aspect = windowWidth.value / windowHeight.value;
const route = useRoute();

const { data: game } = await useAsyncData("game", () =>
  api(`/game/${route.params.id}/`),
);
const { data: lobby } = await useAsyncData("lobby", () =>
  api(`/game/${route.params.id}/lobby/`),
);
const { data: boardStructure } = await useAsyncData("board", () =>
  api(`/board/${toValue(game).board_id}/`),
);

definePageMeta({
  layout: "full",
});

onMounted(async () => {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xeaeaea);

  const camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
  camera.position.set(0, 90, 0);

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    canvas: canvas.value,
  });
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  watch(
    [windowWidth, windowHeight],
    ([newWidth, newHeight]) => {
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    },
    { immediate: true },
  );

  const light = new THREE.AmbientLight(0xffffff, Math.PI);
  scene.add(light);

  const controls = new OrbitControls(camera, canvas.value);
  controls.update();

  const board = new Board(toValue(boardStructure), scene);
  scene.add(board.model);

  await Promise.all(
    lobby.value.map((participation) =>
      board.addCharacter({
        model: participation.character.url,
        target: participation.current_tile,
        identifier: participation.pk,
      }),
    ),
  );

  const characterMovedMessaged = computed(
    () => `game/${route.params.id}/moved`,
  );
  onMessage(characterMovedMessaged, ({ id, tile }) => {
    board.moveCharacter(id, tile);
  });

  const clock = new YUKA.Time();
  renderer.setAnimationLoop(() => {
    const delta = clock.update().getDelta();
    board.update(delta);
    renderer.render(scene, camera);
  });
});
</script>
