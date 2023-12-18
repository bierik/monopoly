<template>
  {{ $route.params.id }}
</template>
<script setup>
const api = useApi()
const route = useRoute()

const { data } = await api(`/game/${route.params.id}/`).get().json()
</script>
