<template>
  <form @submit.prevent="joinGame" class="h-full w-full">
    <div class="grid grid-cols-2 gap-4">
      <div
        class="card aspect-square active:scale-95 duration-300 transition-all overflow-hidden"
        :class="character.pk === selectedCharacter ? 'bg-primary' : 'bg-slate-300'"
        v-for="character in characters"
      >
        <input
          class="hidden"
          type="radio"
          :id="`character-${character.pk}`"
          :value="character.pk"
          v-model="selectedCharacter"
        />
        <label class="flex flex-grow items-center justify-center" :for="`character-${character.pk}`">
          <Suspense>
            <GLTFViewer :path="character.url" />
            <template #fallback>
              <span class="loading loading-ring loading-lg" />
            </template>
          </Suspense>
        </label>
      </div>
    </div>
    <footer class="footer">
      <button class="btn btn-primary" type="submit">Auswählen</button>
    </footer>
  </form>
</template>
<script setup>
definePageMeta({
  layout: 'full',
})

const route = useRoute()
const router = useRouter()
const api = useApi()

const { data: characters } = await useAsyncData('characters', () => api('/character/'))

const selectedCharacter = ref()

async function joinGame() {
  const participation = await api(`/game/${route.params.id}/join/`, {
    method: 'POST',
    body: { character: toValue(selectedCharacter) },
  })
  router.replace({
    name: 'game-id',
    params: { id: route.params.id },
    query: { participation_id: toValue(participation).pk },
  })
}
</script>
