<template>
  <NuxtLayout name="full">
    <canvas ref="canvas" />
  </NuxtLayout>
</template>
<script setup>
import Board from "@/board";
import { useWindowSize } from "@vueuse/core";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { Time } from "yuka";
import {
  Scene,
  PerspectiveCamera,
  WebGLRenderer,
  SRGBColorSpace,
  Color,
  AmbientLight,
  AxesHelper,
} from "three";

const canvas = ref(null);
const { width: windowWidth, height: windowHeight } = useWindowSize();
const aspect = windowWidth.value / windowHeight.value;
const route = useRoute();

const { data: game } = await useAsyncData("game", () =>
  api(`/game/${route.params.id}`),
);
const { data: lobby } = await useAsyncData("lobby", () =>
  api(`/game/${route.params.id}/lobby`),
);
const { data: boardStructure } = await useAsyncData("board", () =>
  api(`/board/${toValue(game).board_id}`),
);

onMounted(async () => {
  const scene = new Scene();
  scene.background = new Color(0xeaeaea);

  scene.add(new AxesHelper(10));

  const camera = new PerspectiveCamera(75, aspect, 0.1, 1000);
  camera.position.set(0, 90, 0);

  const renderer = new WebGLRenderer({
    antialias: true,
    canvas: canvas.value,
  });
  renderer.outputColorSpace = SRGBColorSpace;

  watch(
    [windowWidth, windowHeight],
    ([newWidth, newHeight]) => {
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    },
    { immediate: true },
  );

  const light = new AmbientLight(0xffffff, Math.PI);
  scene.add(light);

  const controls = new OrbitControls(camera, canvas.value);
  controls.update();

  const board = new Board(toValue(boardStructure));
  scene.add(board.model);

  await Promise.all(
    lobby.value.map((participation) =>
      board.addCharacter({
        model: participation.character.url,
        target: participation.current_tile,
        identifier: participation.pk,
        scale: 0.6,
      }),
    ),
  );

  const characterMovedMessaged = computed(
    () => `game/${route.params.id}/moved`,
  );
  onMessage(characterMovedMessaged, ({ id, tile }) => {
    board.moveCharacter(id, tile);
  });

  const clock = new Time();
  renderer.setAnimationLoop(() => {
    const delta = clock.update().getDelta();
    board.update(delta);
    renderer.render(scene, camera);
  });
});
</script>
