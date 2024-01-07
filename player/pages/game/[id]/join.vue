<template>
  <form @submit.prevent="joinGame" class="h-full w-full">
    <div class="grid grid-cols-3 gap-4">
      <label
        v-for="character in characters"
        class="pb-4 card aspect-square active:scale-95 duration-300 transition-all overflow-hidden flex items-center justify-center"
        :for="`character-${character.pk}`"
        :class="character.pk === selectedCharacter ? 'bg-primary' : 'bg-slate-300'"
      >
        <Suspense>
          <GLTFViewer :path="character.url" />
          <template #fallback>
            <span class="loading loading-ring loading-lg" />
          </template>
        </Suspense>
        <span class="font-bold">{{ character.name }}</span>
        <input
          class="hidden"
          type="radio"
          :id="`character-${character.pk}`"
          :value="character.pk"
          v-model="selectedCharacter"
        />
      </label>
    </div>
    <button class="btn btn-primary fixed bottom-4 right-4 drop-shadow-xl" type="submit">Auswählen</button>
  </form>
</template>
<script setup>
definePageMeta({
  layout: 'full',
})

const route = useRoute()
const router = useRouter()

const { data: characters } = await useAsyncData('characters', () => api('/character/'))

const selectedCharacter = ref()

async function joinGame() {
  await api(`/game/${route.params.id}/join/`, {
    method: 'POST',
    body: { character: toValue(selectedCharacter) },
  })
  router.replace({
    name: 'game-id',
    params: { id: route.params.id },
  })
}
</script>
