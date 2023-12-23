<template>
  <div class="container mx-auto h-screen flex flex-col justify-center px-4">
    <div class="card">
      <form @submit.prevent="createGame" class="flex flex-col">
        <input type="number" placeholder="Wie viele Teilnehmende?" class="input w-full mb-4 ghost" />
        <button type="submit" class="btn btn-primary">Erstellen</button>
      </form>
    </div>
  </div>
</template>
<script setup>
const api = useApi()
const router = useRouter()
const route = useRoute()

async function createGame() {
  await api('/login').post({ username: 'admin', password: 'admin' })
  const { data } = await api('/game/', { headers: { 'X-Device-Token': route.params.token } })
    .post()
    .json()
  router.push({ name: 'game-id', params: { id: data.value.pk } })
}
</script>
