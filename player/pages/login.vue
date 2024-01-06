<template>
  <form @submit.prevent="login">
    <div class="card">
      <input autofocus type="text" v-model="username" placeholder="Benutzername" class="input w-full mb-4 outline" />
      <input type="password" v-model="password" placeholder="Passwort" class="input w-full mb-4 outline" />
      <input type="submit" class="btn btn-primary" value="Anmelden" />
    </div>
  </form>
</template>
<script setup>
definePageMeta({
  layout: 'full',
})

const router = useRouter()
const route = useRoute()

const next = route.query.next

const username = ref('')
const password = ref('')

async function login() {
  await api('/login/', { method: 'POST', body: { username: toValue(username), password: toValue(password) } })
  if (!next) {
    router.replace({ name: 'index' })
  } else {
    router.replace(next)
  }
}
</script>
