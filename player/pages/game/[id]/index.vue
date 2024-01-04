<template>
  {{ game }}
  <button @click="startGame" class="btn btn-primary" v-if="isOwner">Starten</button>
</template>
<script setup>
definePageMeta({
  layout: 'full',
})
const route = useRoute()
const router = useRouter()
const api = useApi()
const user = useUserStore()
const onMessage = useOnMessage()

const { data: game } = await useAsyncData('game', () => api(`/game/${route.params.id}/`))

if (toValue(game).status === 'RUNNING') {
  debugger
  router.replace({ name: 'participation-id-play', params: { id: route.query.participation_id } })
}

async function startGame() {
  await api(`/game/${route.params.id}/start/`, { method: 'POST' })
}

const gameStartedMessage = computed(() => `game/${route.params.id}/started`)

onMessage(gameStartedMessage, () => {
  router.replace({ name: 'participation-id-play', params: { id: route.query.participation_id } })
})

const isOwner = toValue(game).owner_id === user.pk
</script>
