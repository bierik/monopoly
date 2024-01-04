export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,
  nitro: {
    devProxy: {
      '/api/': {
        target: 'http://gamemaster:8000/api/',
      },
      '/media/': {
        target: 'http://gamemaster:8000/media/',
      },
    },
  },
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', 'nuxt-icon'],
})
