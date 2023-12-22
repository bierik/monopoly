import { useLocalStorage } from '@vueuse/core'

const deviceToken = useLocalStorage('deviceToken')
const route = useRoute()

export function useCreateGameURL() {
  return `http://localhost:5005/create_game/${toValue(deviceToken)}`
}

export function useCreateJoinGameURL() {
  return `http://localhost:5005/game/${route.params.id}/join`
}
