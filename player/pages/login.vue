<template>
  <div class="container mx-auto flex items-center justify-center h-screen">
    <form @submit.prevent="login">
      <div class="card">
        <input type="text" v-model="username" placeholder="Benutzername" class="input w-full mb-4 outline" />
        <input type="password" v-model="password" placeholder="Passwort" class="input w-full mb-4 outline" />
        <input type="submit" class="btn btn-primary" value="Anmelden" />
      </div>
    </form>
  </div>
</template>
<script setup>
const api = useApi()

const username = ref('')
const password = ref('')

function login() {
  api('/login/', { method: 'POST', body: { username: toValue(username), password: toValue(password) } })
}
</script>
