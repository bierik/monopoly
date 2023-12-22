<template>
  <QrcodeVue v-if="!pending" :value="joinGameURL" />
  {{ joinGameURL }}
  {{ data }}
</template>
<script setup>
import QrcodeVue from 'qrcode.vue'

const api = useApi()
const route = useRoute()
const onMessage = useOnMessage()
const joinGameURL = useCreateJoinGameURL()

const { data, refresh, pending } = await useLazyAsyncData('lobby', () => api(`/game/${route.params.id}/lobby/`))
onMessage(`game/${route.params.id}/joined`, () => {
  refresh()
})
</script>
