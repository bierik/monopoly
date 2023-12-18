import { useLocalStorage, createFetch, useFetch } from '@vueuse/core'
import { useCookies } from '@vueuse/integrations/useCookies'

const { value: deviceToken } = useLocalStorage('deviceToken', null)

await useFetch('/api/csrf').get()

export default createFetch({
  baseUrl: 'http://localhost:5003/api',
  options: {
    async beforeFetch({ options }) {
      if (deviceToken) {
        options.headers['X-Device-Token'] = deviceToken
      }
      const { get } = useCookies('csrftoken')
      options.headers['X-CSRFToken'] = get('csrftoken')
      return {
        options,
      }
    },
  },
})
