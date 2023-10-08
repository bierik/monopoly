<template>
  <button
    class="btn btn-primary"
    data-testid="roll-dice-button"
    :disabled="!canRollDice"
    @click="rollDice"
  >
    Würfeln
  </button>
  <button
    class="btn btn-primary"
    data-testid="end-turn-button"
    :disabled="!canEndTurn"
    @click="endTurn"
  >
    Zug beenden
  </button>
</template>
<script setup>
const route = useRoute();

const { data: participation, refresh: refreshParticipation } =
  await useAsyncData("participation", () =>
    api(`/game/${route.params.id}/participation/`),
  );
const participationChangedMessage = computed(
  () => `participation/${toValue(participation).pk}/changed`,
);
const gameChangedMessage = computed(() => `game/${route.params.id}/changed`);
const canEndTurn = computed(() => toValue(participation).state === "moved");
const canRollDice = computed(
  () =>
    toValue(participation).state === "idle" &&
    toValue(participation).is_players_turn,
);

onMessage(participationChangedMessage, refreshParticipation);
onMessage(gameChangedMessage, refreshParticipation);

async function rollDice() {
  await api(`/participation/${toValue(participation).pk}/move/`, {
    method: "POST",
  });
}

async function endTurn() {
  await api(`/participation/${toValue(participation).pk}/end_turn/`, {
    method: "POST",
  });
}
</script>
