<template>
  <h1 class="text-2xl mb-4">Neues Spiel erstellen</h1>
  <form @submit.prevent="createGame" class="flex flex-col">
    <input
      autofocus
      type="number"
      v-model="maxParticipations"
      placeholder="Anzahl Spieler"
      class="input w-full mb-4 outline"
    />
    <button type="submit" class="btn btn-primary">Erstellen</button>
  </form>
</template>
<script setup>
definePageMeta({
  layout: 'full',
})

const api = useApi()
const router = useRouter()
const route = useRoute()

const maxParticipations = ref()

async function createGame() {
  const game = await api('/game/', {
    body: { max_participations: toValue(maxParticipations) },
    method: 'POST',
    headers: { 'X-Device-Token': route.params.token },
  })
  router.push({ name: 'game-id-join', params: { id: game.pk } })
}
</script>
