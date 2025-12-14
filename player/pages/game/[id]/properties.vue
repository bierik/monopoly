<template>
  <NuxtLayout>
    {{ participation }}
  </NuxtLayout>
</template>
<script setup>
const route = useRoute();
const { data: participation } = useAsyncData("participation", () =>
  api(`/game/${route.params.id}/participation`),
);
</script>
