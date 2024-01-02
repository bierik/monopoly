<template>
  <header class="navbar bg-base-100">
    <div class="flex-1">
      <a class="btn btn-ghost text-xl">daisyUI</a>
    </div>
    <div class="dropdown dropdown-end" v-if="user.username">
      <div tabindex="0" role="button" class="btn m-1">{{ user.username }}</div>
      <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-primary text-primary-content rounded-box">
        <li><a @click="logout">Logout</a></li>
      </ul>
    </div>
  </header>
</template>
<script setup>
const user = useUserStore()
const api = useApi()
const router = useRouter()

async function logout() {
  await api('/logout/', { method: 'POST' })
  router.replace({ name: 'login' })
}
</script>
