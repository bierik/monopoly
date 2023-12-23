import { useLocalStorage } from '@vueuse/core'

await $fetch('/api/csrf')

const deviceToken = toValue(useLocalStorage('deviceToken', null))
const headers = {
  'X-CSRFToken': toValue(useCookie('csrftoken')),
}
if (deviceToken) {
  headers['X-Device-Token'] = deviceToken
}
const api = $fetch.create({ baseURL: '/api', headers })

export default function () {
  return api
}
