<template>
  <div class="container mx-auto h-screen flex flex-col justify-center items-center px-4">
    <h1 class="text-2xl mb-8">Neues Spiel</h1>
    <a :href="createGameURL">
      <QrcodeVue class="qr-code" background="transparent" render-as="svg" :size="200" :value="createGameURL" />
    </a>
  </div>
</template>
<script setup>
import { createCreateGameURL } from '@/url'

const router = useRouter()
const onMessage = useOnMessage()
const api = useApi()

const { data } = await useAsyncData('register-device', () => api('/device/register/', { method: 'POST' }))
useDeviceToken().value = toValue(data).token

const createdGameMessage = computed(() => `${toValue(data).token}/game/created`)
const createGameURL = computed(() => createCreateGameURL(useDeviceToken()))

onMessage(createdGameMessage, ({ game_id: gameId }) => {
  router.replace({ name: 'lobby-id', params: { id: gameId } })
})
</script>
<style>
.qr-code > path + path {
  fill: white;
}
@media (prefers-color-scheme: light) {
  .qr-code > path + path {
    fill: black;
  }
}
</style>
