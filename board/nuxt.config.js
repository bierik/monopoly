import { defineNuxtConfig } from "nuxt/config";

export default defineNuxtConfig({
  devtools: { enabled: false },
  ssr: false,
  app: {
    baseURL: "/board/",
  },
  modules: ["@nuxtjs/tailwindcss", "@nuxt/icon", "@nuxt/eslint"],
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
        "mqtt",
        "three/addons/loaders/GLTFLoader.js",
      ],
    },
    build: {
      target: "esnext",
    },
  },
  experimental: {
    scanPageMeta: false,
  },
});
