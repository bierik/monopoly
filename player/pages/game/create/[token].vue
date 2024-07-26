<template>
  <NuxtLayout name="full">
    <h1 class="mb-4 text-2xl">Neues Spiel erstellen</h1>
    <form class="flex flex-col" @submit.prevent="createGame">
      <label class="form-control w-full">
        <div class="label">
          <span class="label-text">Anzahl Spieler</span>
        </div>
        <input
          v-model="maxParticipations"
          autofocus
          type="number"
          class="input w-full outline"
        />
      </label>
      <label class="form-control w-full">
        <div class="label">
          <span class="label-text">Spielbrett</span>
        </div>
        <select
          v-model="board"
          placeholder="Spielbrett"
          class="select w-full outline"
        >
          <option
            v-for="boardOption in boards"
            :key="boardOption.pk"
            :value="boardOption.pk"
          >
            {{ boardOption.name }}
          </option>
        </select>
      </label>
      <label class="form-control w-full">
        <div class="label">
          <span class="label-text">Startkapital</span>
        </div>
        <input
          v-model.number="initialBalance"
          type="range"
          :min="minBalance"
          :max="maxBalance"
          :step="stepBalance"
          class="range range-primary"
        />
        <div class="flex w-full justify-between px-2 text-xs">
          <span v-for="measure in balanceMeasures" :key="measure">{{
            measure
          }}</span>
        </div>
      </label>
      <button
        type="submit"
        data-testid="create-new-game-button"
        class="btn btn-primary mt-4"
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

const boards = await api("/board/");
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
  const game = await api("/game/", {
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
