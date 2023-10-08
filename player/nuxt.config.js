import { defineNuxtConfig } from "nuxt/config";

export default defineNuxtConfig({
  devtools: { enabled: false },
  ssr: false,
  app: {
    baseURL: "/player/",
  },
  vite: {
    server: {
      hmr: {
        path: "hmr/",
      },
    },
    // Pevents dev server from reloading
    optimizeDeps: {
      include: [
        "three",
        "@vueuse/core",
        "lodash-es",
        "three/addons/loaders/GLTFLoader.js",
        "mqtt",
      ],
    },
    build: {
      target: "esnext",
    },
  },
  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt", "@nuxt/icon", "@nuxt/eslint"],
  experimental: {
    scanPageMeta: false,
  },
});
