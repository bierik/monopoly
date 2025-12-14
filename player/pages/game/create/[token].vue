<template>
  <NuxtLayout name="full">
    <h1 class="mb-4 text-2xl">Neues Spiel erstellen</h1>
    <form @submit.prevent="createGame">
      <fieldset class="fieldset">
        <label class="label" for="max-participations">
          <span>Anzahl Spieler</span>
        </label>
        <input
          id="max-participations"
          v-model="maxParticipations"
          autofocus
          type="number"
          class="input outline"
        />
        <label class="label" for="board">
          <span>Spielbrett</span>
        </label>
        <select
          id="board"
          v-model="board"
          placeholder="Spielbrett"
          class="select outline"
        >
          <option
            v-for="boardOption in boards"
            :key="boardOption.pk"
            :value="boardOption.pk"
          >
            {{ boardOption.name }}
          </option>
        </select>
        <label class="label" for="balance">
          <span>Startkapital</span>
        </label>
        <input
          id="balance"
          v-model.number="initialBalance"
          type="range"
          :min="minBalance"
          :max="maxBalance"
          :step="stepBalance"
          class="range range-primary"
        />
        <div class="flex justify-between px-2 text-xs">
          <span v-for="measure in balanceMeasures" :key="measure">{{
            measure
          }}</span>
        </div>
      </fieldset>
      <button
        type="submit"
        data-testid="create-new-game-button"
        class="btn btn-primary mt-4 w-full"
      >
        Erstellen
      </button>
    </form>
  </NuxtLayout>
</template>
<script setup>
import { first, range } from "lodash-es";
import { toValue } from "vue";

const router = useRouter();
const route = useRoute();

const compactNumberFormatter = new Intl.NumberFormat("en", {
  notation: "compact",
});

const boards = await api("/board");
const maxParticipations = ref();
const board = ref(first(boards).pk);
const initialBalance = ref(3000);
const minBalance = 1000;
const maxBalance = 5000;
const stepBalance = 500;
const balanceMeasures = range(minBalance, maxBalance + stepBalance, stepBalance)
  .filter((step) => step % 1000 === 0)
  .map(compactNumberFormatter.format);

async function createGame() {
  const game = await api("/game", {
    body: {
      max_participations: toValue(maxParticipations),
      board: toValue(board),
      initial_balance: toValue(initialBalance),
    },
    method: "POST",
    headers: { "X-Device-Token": route.params.token },
  });
  router.push({ name: "game-id-join", params: { id: game.pk } });
}
</script>
