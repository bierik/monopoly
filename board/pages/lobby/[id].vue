<template>
  <div class="container mx-auto h-screen flex flex-col justify-center items-center px-4">
    <a :href="joinGameURL" class="mb-12">
      <QrcodeVue
        :size="200"
        class="qr-code"
        :value="joinGameURL"
        background="transparent"
        foreground="white"
        render-as="svg"
      />
    </a>
    <div class="grid gap-4 grid-cols-4 grid-rows-1">
      <div class="card bg-slate-200 flex justify-center items-center" v-for="participation in lobby">
        {{ participation.player.username }}
      </div>
      <div class="card bg-slate-400 p-12" v-for="_ in missingParticipations">
        <Icon :size="50" class="animate-spin" name="mdi-light:loading" />
      </div>
    </div>
  </div>
</template>
<script setup>
import QrcodeVue from 'qrcode.vue'
import { createJoinGameURL } from '@/url'
import size from 'lodash/size'
import { toValue } from 'vue'

const api = useApi()
const route = useRoute()
const onMessage = useOnMessage()

const { data: lobby, refresh: refreshLobby } = await useAsyncData('lobby', () => api(`/game/${route.params.id}/lobby/`))
const { data: game } = await useAsyncData('game', () => api(`/game/${route.params.id}/`))

const joinGameMessage = computed(() => `game/${route.params.id}/joined`)
const joinGameURL = computed(() => createJoinGameURL(route.params.id))
const missingParticipations = computed(() => toValue(game).max_participations - size(toValue(lobby)))

onMessage(joinGameMessage, () => {
  refreshLobby()
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
