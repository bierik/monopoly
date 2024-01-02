<template>
  <div class="card">
    <form @submit.prevent="createGame" class="flex flex-col">
      <input
        type="number"
        v-model="maxParticipations"
        placeholder="Anzahl Spieler?"
        class="input w-full mb-4 outline"
      />
      <button type="submit" class="btn btn-primary">Erstellen</button>
    </form>
  </div>
</template>
<script setup>
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
  router.push({ name: 'game-id', params: { id: game.pk } })
}
</script>
