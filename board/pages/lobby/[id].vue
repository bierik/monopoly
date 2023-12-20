<template>
  <QrcodeVue :value="joinGameURL" />
  {{ joinGameURL }}
</template>
<script setup>
import QrcodeVue from 'qrcode.vue'

const api = useApi()
const route = useRoute()
const onMessage = useOnMessage()

const { data } = await api(`/game/${route.params.id}/`).get().json()
const joinGameURL = `http://localhost:5005/game/${route.params.id}/join`
onMessage(`game/${route.params.id}/joined`, () => {
  console.log('joined')
})
</script>
