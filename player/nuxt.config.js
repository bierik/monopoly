export default defineNuxtConfig({
  devtools: { enabled: true },
  nitro: {
    devProxy: {
      "/api/": {
        target: "http://gamemaster:8000/api/",
      },
    },
  },
});
