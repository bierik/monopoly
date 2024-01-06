await $fetch('/api/csrf/')

const headers = {
  'X-CSRFToken': toValue(useCookie('csrftoken')),
}
export default $fetch.create({ baseURL: '/api', headers })
