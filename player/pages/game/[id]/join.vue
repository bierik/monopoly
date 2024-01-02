<template>
  <form @submit.prevent="joinGame">
    <div class="grid grid-cols-3 gap-4">
      <div
        class="card bg-white aspect-square active:scale-95 duration-300 transition-all overflow-hidden"
        :class="{ 'bg-primary': character.pk === selectedCharacter }"
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
    <button class="btn btn-primary" type="submit">Auswählen</button>
  </form>
</template>
<script setup>
const route = useRoute()
const api = useApi()

const { data: characters } = await useAsyncData('characters', () => api('/character/'))

const selectedCharacter = ref()

async function joinGame() {
  const { data } = await api(`/game/${route.params.id}/join/`, {
    method: 'POST',
    body: { character: toValue(selectedCharacter) },
  })
}
</script>
