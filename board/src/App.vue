<template>
  <canvas ref="canvas" />
</template>
<script setup>
import * as THREE from 'three'
import { onMounted, watch, ref } from 'vue'
import Board from '@/board'
import { useWindowSize, useFetch } from '@vueuse/core'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import * as YUKA from 'yuka'
import mqtt from 'mqtt'

const canvas = ref(null)
const { width: windowWidth, height: windowHeight } = useWindowSize()
const aspect = windowWidth.value / windowHeight.value

onMounted(async () => {
  const scene = new THREE.Scene()
  scene.background = new THREE.Color(0xeaeaea)

  const camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000)
  camera.position.set(80, 40, 100)

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    canvas: canvas.value,
  })
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.setSize(windowWidth.value, windowHeight.value)

  watch([windowWidth, windowHeight], ([newWidth, newHeight]) => {
    camera.aspect = newWidth / newHeight
    camera.updateProjectionMatrix()
    renderer.setSize(newWidth, newHeight)
  })

  const light = new THREE.AmbientLight(0xffffff, Math.PI)
  scene.add(light)

  const controls = new OrbitControls(camera, canvas.value)
  controls.update()

  const { data: nodeLinkGraph } = await useFetch('http://localhost:5002/api/board/monopoly/').get().json()

  const board = Board.fromNodeLinkGraph(nodeLinkGraph.value, scene)
  scene.add(board.model)

  const casualMale = await board.addCharacter({ name: 'casual_male' })
  // casualMale.goTo('start')

  // const client = mqtt.connect('mqtt://localhost:5001')
  // client.on('connect', () => {
  //   client.subscribe('bla', (err) => {
  //     console.log(err)
  //   })
  // })
  // client.on('message', (topic, message) => {
  //   console.log(topic)
  //   console.log(message.toString())
  // })

  const clock = new YUKA.Time()
  renderer.setAnimationLoop(() => {
    const delta = clock.update().getDelta()
    board.update(delta)
    renderer.render(scene, camera)
  })
})
</script>
