<template>
  <div class="container mx-auto h-screen flex flex-col justify-center items-center px-4">
    <a :href="joinGameURL">
      <QrcodeVue :size="200" :value="joinGameURL" background="transparent" foreground="white" render-as="svg" />
    </a>
    <div class="flex">
      <div class="card">loading</div>
    </div>
  </div>
  {{ data }}
</template>
<script setup>
import QrcodeVue from 'qrcode.vue'
import { createJoinGameURL } from '@/url'

const api = useApi()
const route = useRoute()
const onMessage = useOnMessage()

const { data, refresh } = await useLazyAsyncData('lobby', () => api(`/game/${route.params.id}/lobby/`))

const joinGameMessage = computed(() => `game/${route.params.id}/joined`)
const joinGameURL = computed(() => createJoinGameURL(route.params.id))

onMessage(joinGameMessage, () => {
  refresh()
})
</script>
