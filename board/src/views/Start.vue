<template>
  <Suspense>
    <CreateGameCode />
    <template #fallback> loading </template>
  </Suspense>
</template>
<script setup>
import CreateGameCode from '@/components/CreateGameCode.vue'
</script>
