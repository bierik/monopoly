<template>
  <QrcodeVue value="https://example.com" />
  {{ createGameURL }}
</template>
<script setup>
import api from '@/api'
import { useLocalStorage } from '@vueuse/core'
import get from 'lodash/get'
import QrcodeVue from 'qrcode.vue'
import mqtt from '@/mqtt_client'
import { onMounted } from 'vue'

const deviceToken = useLocalStorage('deviceToken')
const { data } = await api(`/device/register/`).post().json()
deviceToken.value = get(data, 'value.token', null)

const createGameURL = `http://localhost:5005/create_game/${deviceToken.value}`

onMounted(async () => {
  await mqtt.subscribe('game/created')
  mqtt.on('game/created', (message) => {
    console.log(message)
  })
})
</script>
