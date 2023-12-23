<template>
  <form @submit.prevent="createGame">
    <button class="btn btn-primary">Button</button>
    <input type="submit" value="abla" />
  </form>
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
