import { createFetch, useFetch } from '@vueuse/core'

await useFetch('/api/csrf').get()

const api = createFetch({
  baseUrl: '/api',
  options: {
    beforeFetch({ options }) {
      const { value: csrfToken } = useCookie('csrftoken')
      options.headers = {
        ...options.headers,
        'X-CSRFToken': csrfToken,
      }
      return { options }
    },
  },
})

export default function () {
  return api
}
