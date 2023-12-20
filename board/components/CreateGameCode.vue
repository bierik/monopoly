<template>
  <QrcodeVue :value="createGameURL" />
  {{ createGameURL }}
</template>
<script setup>
import { useLocalStorage } from '@vueuse/core'
import get from 'lodash/get'
import QrcodeVue from 'qrcode.vue'

const router = useRouter()
const api = useApi()
const onMessage = useOnMessage()
const deviceToken = useLocalStorage('deviceToken')

const { data } = await api(`/device/register/`).post().json()
deviceToken.value = get(data, 'value.token', null)

const createGameURL = `http://localhost:5005/create_game/${deviceToken.value}`

onMessage(`${deviceToken.value}/game/created`, ({ game_id: gameId }) => {
  router.replace({ name: 'lobby-id', params: { id: gameId } })
})
</script>
