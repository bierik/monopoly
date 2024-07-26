<template>
  <NuxtLayout name="full">
    <h1 class="mb-4 text-2xl">Registrieren</h1>
    <p class="mb-4 text-center text-sm">
      QR-Code scannen, um ein Spiel zu starten
    </p>
    <a :href="createGameURL" data-testid="create-game-link">
      <QrcodeVue
        background="transparent"
        render-as="svg"
        :size="200"
        :value="createGameURL"
      />
    </a>
  </NuxtLayout>
</template>
<script setup>
import { createCreateGameURL } from "@/url";

const router = useRouter();

const { data } = await useAsyncData("register-device", () =>
  api("/device/register/", { method: "POST" }),
);
useDeviceToken().value = toValue(data).token;

const createdGameMessage = computed(
  () => `${toValue(data).token}/game/created`,
);
const createGameURL = computed(() => createCreateGameURL(toValue(data).token));

onMessage(createdGameMessage, ({ id }) => {
  router.push({ name: "lobby-id", params: { id } });
});
</script>
