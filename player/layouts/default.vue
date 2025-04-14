<template>
  <div class="navbar bg-base-100">
    <div class="flex-1 text-xl">monopoly</div>
    <div class="flex-none">
      <span data-testid="participation-balance">{{ balance }}</span>
    </div>
  </div>
  <div class="container mx-auto p-2">
    <slot />
  </div>
  <div class="dock">
    <nuxt-link
      class="text-primary"
      active-class="active"
      :to="{ name: 'game-id-play', params: { id: route.params.id } }"
    >
      <Icon name="material-symbols-light:play-arrow-rounded" size="40" />
    </nuxt-link>
    <nuxt-link
      class="text-primary"
      active-class="active"
      :to="{ name: 'game-id-properties', params: { id: route.params.id } }"
    >
      <Icon name="material-symbols-light:house-outline-rounded" size="40" />
    </nuxt-link>
    <nuxt-link
      class="text-primary"
      active-class="active"
      :to="{ name: 'game-id-account', params: { id: route.params.id } }"
    >
      <Icon name="material-symbols-light:person" size="40" />
    </nuxt-link>
  </div>
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

onMessage(participationChangedMessage, refreshParticipation);
onMessage(gameChangedMessage, refreshParticipation);

const balance = computed(() => toCurrency(toValue(participation).balance));
</script>
