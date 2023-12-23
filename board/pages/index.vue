<template>
  <QrcodeVue v-if="!pending" :value="createGameURL" />
  {{ createGameURL }}
</template>
<script setup>
import { createCreateGameURL } from '@/url'

const router = useRouter()
const onMessage = useOnMessage()
const api = useApi()
import get from 'lodash/get'

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
