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
const user = useUserStore()
const onMessage = useOnMessage()

const { data: game } = await useAsyncData('game', () => api(`/game/${route.params.id}/`))

if (toValue(game).status === 'RUNNING') {
  router.push({ name: 'game-id-play', params: { id: game.pk } })
}

async function startGame() {
  await api(`/game/${route.params.id}/start/`, { method: 'POST' })
}

const gameStartedMessage = computed(() => `game/${route.params.id}/started`)

onMessage(gameStartedMessage, () => {
  router.push({ name: 'game-id-play', params: { id: game.pk } })
})

const isOwner = toValue(game).owner_id === user.pk
</script>
