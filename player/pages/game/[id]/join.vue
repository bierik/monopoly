<template>
  <form class="size-full" @submit.prevent="joinGame">
    <div class="grid grid-cols-3 gap-4">
      <label
        v-for="character in characters"
        :key="character.identifier"
        class="card flex aspect-square items-center justify-center overflow-hidden pb-4 transition-all duration-300 active:scale-95"
        :for="`character-${character.pk}`"
        :class="
          character.pk === selectedCharacter ? 'bg-primary' : 'bg-slate-300'
        "
      >
        <Suspense>
          <GLTFViewer :path="character.url" />
          <template #fallback>
            <span class="loading loading-ring loading-lg" />
          </template>
        </Suspense>
        <span class="font-bold" data-testid="character-name">{{
          character.name
        }}</span>
        <input
          :id="`character-${character.pk}`"
          v-model="selectedCharacter"
          class="hidden"
          type="radio"
          :value="character.pk"
        />
      </label>
    </div>
    <button
      class="btn btn-primary fixed bottom-4 right-4 drop-shadow-xl"
      type="submit"
      data-testid="select-character-button"
    >
      Auswählen
    </button>
  </form>
</template>
<script setup>
definePageMeta({
  layout: "full",
});

const route = useRoute();
const router = useRouter();

const { data: characters } = await useAsyncData("characters", () =>
  api("/character/"),
);

const selectedCharacter = ref();

async function joinGame() {
  await api(`/game/${route.params.id}/join/`, {
    method: "POST",
    body: { character: toValue(selectedCharacter) },
  });
  router.push({
    name: "game-id",
    params: { id: route.params.id },
  });
}
</script>
