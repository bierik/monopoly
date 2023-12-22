<template>
  <QrcodeVue v-if="!pending" :value="createGameURL" />
  {{ createGameURL }}
</template>
<script setup>
import { useLocalStorage } from '@vueuse/core'
const router = useRouter()
const onMessage = useOnMessage()
const createGameURL = useCreateGameURL()
const api = useApi()

const deviceToken = useLocalStorage('deviceToken', null)

const { pending, data } = await useLazyAsyncData('register-device', () => api('/device/register/', { method: 'POST' }))
watch(data, () => {
  deviceToken.value = toValue(data).token
  onMessage(`${toValue(data).token}/game/created`, ({ game_id: gameId }) => {
    router.replace({ name: 'lobby-id', params: { id: gameId } })
  })
})
</script>
