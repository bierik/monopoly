await $fetch('/api/csrf/')

const headers = {
  'X-CSRFToken': toValue(useCookie('csrftoken')),
}
const api = $fetch.create({ baseURL: '/api', headers })

export default function () {
  return api
}
