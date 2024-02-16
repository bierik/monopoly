const gamemasterServerUpstream = process.env.MONOPOLY_SERVER_UPSTREAM || 'http://gamemaster:8000'

export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,
  nitro: {
    devProxy: {
      '/api/': {
        target: `${gamemasterServerUpstream}/api/`,
      },
      '/media/': {
        target: `${gamemasterServerUpstream}/media/`,
      },
    },
  },
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', 'nuxt-icon'],
})
