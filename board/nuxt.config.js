import { defineNuxtConfig } from "nuxt/config";
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  devtools: { enabled: false },
  ssr: false,
  modules: ["@nuxt/icon", "@nuxt/eslint"],
  css: ["./assets/css/tailwind.css"],
  vite: {
    plugins: [tailwindcss()],
    server: {
      hmr: {
        path: "hmr/",
      },
    },
    // Pevents dev server from reloading
    optimizeDeps: {
      include: [
        "qrcode.vue",
        "three",
        "@vueuse/core",
        "lodash-es",
        "mqtt",
        "three/addons/loaders/GLTFLoader.js",
        "three/addons/controls/OrbitControls.js",
        "yuka",
      ],
    },
    build: {
      target: "esnext",
    },
  },
});
