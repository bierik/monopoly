<template>
  <div class="container mx-auto p-2">
    <slot />
  </div>
  <div class="btm-nav">
    <nuxt-link class="text-primary" active-class="active" :to="{ name: 'index' }">
      <Icon name="material-symbols-light:play-arrow-rounded" size="40" />
    </nuxt-link>
    <nuxt-link class="text-primary" active-class="active" :to="{ name: 'properties' }">
      <Icon name="material-symbols-light:house-outline-rounded" size="40" />
    </nuxt-link>
    <nuxt-link class="text-primary" active-class="active" :to="{ name: 'account' }">
      <Icon name="material-symbols-light:person" size="40" />
    </nuxt-link>
  </div>
</template>
<script setup></script>
