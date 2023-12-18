<template>
  <form @submit.prevent="createGame">
    <input type="text" v-model="character" />
    <input type="submit" value="abla" />
  </form>
</template>
<script setup>
const api = useApi()
const router = useRouter()

const character = ref('')

async function createGame() {
  await api('/login').post({ username: 'admin', password: 'admin' })
  const { data } = await api('/game/').post({ character: character.value }).json()
  router.push({ name: 'game-id', params: { id: data.value.pk } })
}
</script>
