import { useLocalStorage, createFetch, useFetch } from '@vueuse/core'

const { value: deviceToken } = useLocalStorage('deviceToken', null)

const api = createFetch({
  baseUrl: '/api',
  options: {
    async beforeFetch({ options }) {
      if (deviceToken) {
        options.headers['X-Device-Token'] = deviceToken
      }
      const { value: csrfToken } = useCookie('csrftoken')
      options.headers['X-CSRFToken'] = csrfToken
      return {
        options,
      }
    },
  },
})

export default function () {
  return api
}
