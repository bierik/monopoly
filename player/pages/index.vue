<template>
  <h1 class="mb-4 text-2xl">Willkommmen</h1>
  <p class="text-center text-sm mb-4">QR-Code scannen, um ein Spiel zu erstellen oder einem Spiel beizutreten.</p>
  <div>
    <QRCodeScanner />
  </div>
</template>
<script setup>
definePageMeta({
  layout: 'full',
})
</script>
