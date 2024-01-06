import { useLocalStorage } from '@vueuse/core'

await $fetch('/api/csrf/')

const deviceToken = toValue(useLocalStorage('deviceToken', null))
const headers = {
  'X-CSRFToken': toValue(useCookie('csrftoken')),
}
if (deviceToken) {
  headers['X-Device-Token'] = deviceToken
}
export default $fetch.create({ baseURL: '/api', headers })
