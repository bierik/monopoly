<template>
  <h1 class="text-2xl mb-4">Spiel beitreten</h1>
  <a :href="joinGameURL" class="mb-12">
    <QrcodeVue :size="200" class="qr-code" :value="joinGameURL" background="transparent" render-as="svg" />
  </a>
  <div class="flex gap-4">
    <div class="card bg-slate-200 flex justify-center items-center w-48 h-48 p-8" v-for="participation in lobby">
      <GLTFViewer :path="participation.character.url" />
      <span class="text-xl">{{ participation.player.username }}</span>
    </div>
    <div class="card bg-slate-400 p-12 flex justify-center items-center w-48 h-48" v-for="_ in missingParticipations">
      <span class="loading loading-ring loading-lg text-primary" />
    </div>
  </div>
</template>
<script setup>
import QrcodeVue from 'qrcode.vue'
import { createJoinGameURL } from '@/url'
import size from 'lodash/size'
import { toValue } from 'vue'

definePageMeta({
  layout: 'full',
})

const route = useRoute()
const router = useRouter()
const onMessage = useOnMessage()

const { data: lobby, refresh: refreshLobby } = await useAsyncData('lobby', () => api(`/game/${route.params.id}/lobby/`))
const { data: game } = await useAsyncData('game', () => api(`/game/${route.params.id}/`))

const joinGameMessage = computed(() => `game/${route.params.id}/joined`)
const gameStartedMessage = computed(() => `game/${route.params.id}/started`)
const joinGameURL = computed(() => createJoinGameURL(route.params.id))
const missingParticipations = computed(() => toValue(game).max_participations - size(toValue(lobby)))

onMessage(joinGameMessage, () => {
  refreshLobby()
})
onMessage(gameStartedMessage, () => {
  router.replace({ name: 'game-id', params: { id: route.params.id } })
})
</script>
