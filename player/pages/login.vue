<template>
  <form @submit.prevent="login">
    <input type="text" v-model="username" />
    <input type="password" v-model="password" />
    <input type="submit" value="abla" />
  </form>
</template>
<script setup>
const api = useApi()

const username = ref('')
const password = ref('')

function login() {
  api('/login', { method: 'POST', body: { username, password } })
}
</script>
