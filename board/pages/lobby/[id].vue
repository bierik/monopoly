<template>
  <QrcodeVue v-if="!pending" :value="joinGameURL" />
  {{ joinGameURL }}
  {{ data }}
</template>
<script setup>
import QrcodeVue from 'qrcode.vue'
import { createJoinGameURL } from '@/url'

const api = useApi()
const route = useRoute()
const onMessage = useOnMessage()

const { data, refresh, pending } = await useLazyAsyncData('lobby', () => api(`/game/${route.params.id}/lobby/`))

const joinGameMessage = computed(() => `game/${route.params.id}/joined`)
const joinGameURL = computed(() => createJoinGameURL(route.params.id))

onMessage(joinGameMessage, () => {
  refresh()
})
</script>
