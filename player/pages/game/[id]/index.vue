<template>
  <NuxtLayout name="full">
    <button
      v-if="isOwner"
      class="btn btn-primary"
      data-testid="start-game-button"
      :disabled="!game.is_lobby_full"
      @click="startGame"
    >
      Starten
    </button>
    <div v-else class="flex flex-col items-center justify-center">
      <span class="loading loading-ring loading-lg mb-4 text-primary" />
      <span class="text-xl">Warten auf Spielstart</span>
    </div>
  </NuxtLayout>
</template>
<script setup>
const route = useRoute();
const router = useRouter();
const user = useUserStore();

const { data: game, refresh: refreshGame } = await useAsyncData("game", () =>
  api(`/game/${route.params.id}`),
);

async function startGame() {
  await api(`/game/${route.params.id}/start`, { method: "POST" });
}

const gameChangedMessage = computed(() => `game/${route.params.id}/changed`);
const participationCreatedMessage = computed(() => `participation/created`);
const isOwner = toValue(game).owner_id === user.pk;

onMessage(gameChangedMessage, refreshGame);
onMessage(participationCreatedMessage, refreshGame);

watch(
  game,
  ({ status }) => {
    if (status === "RUNNING") {
      router.push({ name: "game-id-play", params: { id: game.pk } });
    }
  },
  { immediate: true },
);
</script>
