<template>
  <div ref="viewer" class="size-full" />
</template>
<script setup>
import * as THREE from "three";
import { useElementSize } from "@vueuse/core";

const { path } = defineProps({
  path: {
    type: String,
    required: true,
  },
});

const viewer = ref(null);
const { width, height } = useElementSize(viewer);

const aspect = computed(() => width / height);

const { scene: model, animations } = await loadGLTF(path);
const mixer = new THREE.AnimationMixer(model);
const clip = THREE.AnimationClip.findByName(animations, "Walk");
const action = mixer.clipAction(clip);
action.play();

const scene = new THREE.Scene();

const box = new THREE.Box3().setFromObject(model);
const center = new THREE.Vector3();
box.getCenter(center);
model.position.sub(center);
scene.add(model);

const light = new THREE.AmbientLight(0xffffff, Math.PI);
scene.add(light);

const boundingBox = new THREE.Box3().setFromObject(model);
const modelSize = boundingBox.getSize(new THREE.Vector3());
const maxModelSize = Math.max(modelSize.x, modelSize.y, modelSize.z) + 1;
const cameraDistance = maxModelSize / Math.tan(Math.PI / 8);

const camera = new THREE.PerspectiveCamera(75, toValue(aspect), 0.1, 1000);
camera.position.set(0, 1, cameraDistance - 2.5);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setSize(toValue(width), toValue(height));

const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  mixer.update(clock.getDelta());
  renderer.render(scene, camera);
});

watch(
  [width, height],
  ([newWidth, newHeight]) => {
    camera.aspect = newWidth / newHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(newWidth, newHeight);
  },
  { immediate: true },
);
onMounted(() => {
  toValue(viewer).appendChild(renderer.domElement);
});
</script>
