import Start from '@/views/Start.vue'
import Game from '@/views/Game.vue'
import Lobby from '@/views/Lobby.vue'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: Start },
  { path: '/game', component: Game },
  { path: '/lobby/:id', component: Lobby },
]

const router = createRouter({
  routes,
  history: createWebHistory('/'),
})

export default router
