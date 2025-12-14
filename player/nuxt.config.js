import { defineNuxtConfig } from "nuxt/config";
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  devtools: { enabled: false },
  ssr: false,
  modules: ["@pinia/nuxt", "@nuxt/icon", "@nuxt/eslint"],
  css: ["./assets/css/tailwind.css"],
  vite: {
    server: {
      hmr: {
        path: "hmr/",
      },
    },
    plugins: [tailwindcss()],
    // Pevents dev server from reloading
    optimizeDeps: {
      include: [
        "vue-qrcode-reader",
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
