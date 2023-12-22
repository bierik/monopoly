import { useLocalStorage } from '@vueuse/core'

await $fetch('/api/csrf')

const headers = {
  'X-Device-Token': toValue(useLocalStorage('deviceToken', null)),
  'X-CSRFToken': toValue(useCookie('csrftoken')),
}
const api = $fetch.create({ baseURL: '/api', headers })

export default function () {
  return api
}
