import { defineNuxtConfig } from "nuxt/config";

export default defineNuxtConfig({
  extends: ["../common"],
  devtools: { enabled: false },
  ssr: false,
  app: {
    baseURL: "/player/",
  },
  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt", "@nuxt/icon", "@nuxt/eslint"],
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
});
