<template>
  <div class="container mx-auto h-screen flex flex-col justify-center items-center px-4">
    <h1 class="text-2xl mb-8">Neues Spiel</h1>
    <a :href="createGameURL">
      <QrcodeVue
        class="create-game-qrcode"
        background="transparent"
        foreground="white"
        render-as="svg"
        :size="200"
        v-if="!pending"
        :value="createGameURL"
      />
    </a>
  </div>
  {{ createGameURL }}
</template>
<script setup>
import { createCreateGameURL } from '@/url'
import get from 'lodash/get'

const router = useRouter()
const onMessage = useOnMessage()
const api = useApi()

const { pending, data } = await useLazyAsyncData('register-device', () => api('/device/register/', { method: 'POST' }))
const deviceToken = computed(() => get(toValue(data), 'token'))
const createdGameMessage = computed(() => `${toValue(deviceToken)}/game/created`)
const createGameURL = computed(() => createCreateGameURL(deviceToken))

watch(data, () => {
  useDeviceToken().value = toValue(deviceToken)
})

onMessage(createdGameMessage, ({ game_id: gameId }) => {
  router.replace({ name: 'lobby-id', params: { id: gameId } })
})
</script>
