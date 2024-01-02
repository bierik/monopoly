<template>
  <h1 class="text-center text-2xl">Willkommen</h1>
  <QRCodeScanner @new="newGame" @join="joinGame" />
</template>
<script setup>
const router = useRouter()

function newGame(token) {
  router.push({ name: 'game-create-token', params: { token } })
}

function joinGame(gameId) {
  router.push({ name: 'game-id-join', params: { id: gameId } })
}
</script>
