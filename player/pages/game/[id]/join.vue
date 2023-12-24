<template>
  <form @submit.prevent="joinGame">
    <input type="text" v-model="character" />
    <input type="submit" value="abla" />
  </form>
</template>
<script setup>
const route = useRoute()
const api = useApi()

const character = ref('')

async function joinGame() {
  const { data } = await api(`/game/${route.params.id}/join/`, { method: 'POST', body: { character: character.value } })
}
</script>
