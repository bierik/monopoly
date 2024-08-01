<template>
  <NuxtLayout name="full">
    <h1 class="mb-4 text-2xl">Spiel beitreten</h1>
    <a :href="joinGameURL" class="mb-12">
      <QrcodeVue
        :size="200"
        :value="joinGameURL"
        background="transparent"
        render-as="svg"
      />
    </a>
    <div class="flex gap-4">
      <div
        v-for="participation in lobby"
        :key="participation.id"
        class="card flex size-48 items-center justify-center bg-slate-200 p-8"
      >
        <GLTFViewer :path="participation.character.url" />
        <span data-testid="participation-username" class="text-xl">{{
          participation.player.username
        }}</span>
      </div>
      <div
        v-for="missingParticipation in missingParticipations"
        :key="missingParticipation"
        data-testid="missing-participation"
        class="card flex size-48 items-center justify-center bg-slate-400 p-12"
      >
        <span class="loading loading-ring loading-lg text-primary" />
      </div>
    </div>
  </NuxtLayout>
</template>
<script setup>
import QrcodeVue from "qrcode.vue";
import { size } from "lodash-es";

const route = useRoute();
const router = useRouter();

const { data: lobby, refresh: refreshLobby } = await useAsyncData("lobby", () =>
  api(`/game/${route.params.id}/lobby/`),
);
const { data: game, refresh: refreshGame } = await useAsyncData("game", () =>
  api(`/game/${route.params.id}/`),
);

const gameChangesMessage = computed(() => `game/${route.params.id}/changed`);
const participationCreatedMessage = computed(() => "participation/created");
const joinGameURL = computed(() => createJoinGameURL(route.params.id));
const missingParticipations = computed(
  () => toValue(game).max_participations - size(toValue(lobby)),
);

onMessage(gameChangesMessage, refreshGame);

onMessage(participationCreatedMessage, refreshLobby);

watch(
  game,
  ({ status }) => {
    if (status === "RUNNING") {
      router.push({ name: "game-id", params: { id: game.pk } });
    }
  },
  { immediate: true },
);
</script>
