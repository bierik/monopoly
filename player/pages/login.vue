<template>
  <NuxtLayout name="full">
    <form @submit.prevent="login">
      <div class="card">
        <input
          v-model="username"
          autofocus
          type="text"
          placeholder="Benutzername"
          class="input mb-4 outline"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Passwort"
          class="input mb-4 outline"
        />
        <input
          type="submit"
          class="btn btn-primary"
          value="Anmelden"
          data-testid="login-button"
        />
      </div>
    </form>
  </NuxtLayout>
</template>
<script setup>
const router = useRouter();
const route = useRoute();

const next = route.query.next;

const username = ref("");
const password = ref("");

async function login() {
  await api("/login", {
    method: "POST",
    body: { username: toValue(username), password: toValue(password) },
  });
  if (!next) {
    router.push({ name: "index" });
  } else {
    router.push(next);
  }
}
</script>
