<template>
  {{ route.params.id }}
</template>
<script setup>
import api from '@/api'
import { useRoute } from 'vue-router'
const route = useRoute()

const { data } = await api(`/game/${route.params.id}/`).get().json()
console.log(data.value)
</script>
