<template>
  <h1 class="text-2xl mb-4">Registrieren</h1>
  <p class="text-center text-sm mb-4">QR-Code scannen, um ein Spiel zu starten</p>
  <a :href="createGameURL">
    <QrcodeVue class="qr-code" background="transparent" render-as="svg" :size="200" :value="createGameURL" />
  </a>
</template>
<script setup>
import { createCreateGameURL } from '@/url'

definePageMeta({
  layout: 'full',
})

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
