<template>
  <h1 class="text-2xl mb-4">Neues Spiel erstellen</h1>
  <form @submit.prevent="createGame" class="flex flex-col">
    <label class="form-control w-full">
      <div class="label">
        <span class="label-text">Anzahl Spieler</span>
      </div>
      <input autofocus type="number" v-model="maxParticipations" class="input w-full outline" />
    </label>
    <label class="form-control w-full">
      <div class="label">
        <span class="label-text">Spielbrett</span>
      </div>
      <select placeholder="Spielbrett" v-model="board" class="select w-full outline">
        <option v-for="board in boards" :value="board.pk">{{ board.name }}</option>
      </select>
    </label>
    <button type="submit" class="btn btn-primary mt-4">Erstellen</button>
  </form>
</template>
<script setup>
import first from 'lodash/first'
import { toValue } from 'vue'

definePageMeta({
  layout: 'full',
})

const router = useRouter()
const route = useRoute()

const boards = await api('/board/')

const maxParticipations = ref()
const board = ref(first(boards).pk)

async function createGame() {
  const game = await api('/game/', {
    body: { max_participations: toValue(maxParticipations), board: toValue(board) },
    method: 'POST',
    headers: { 'X-Device-Token': route.params.token },
  })
  router.push({ name: 'game-id-join', params: { id: game.pk } })
}
</script>
