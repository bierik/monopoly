import { defineStore } from 'pinia'
import useApi from '@/composables/useApi'

const api = useApi()

export const useUserStore = defineStore({
  id: 'user-store',
  state: () => {
    return {
      username: '',
      name: '',
      pk: null,
    }
  },
  actions: {
    async fetch() {
      const user = await api('/authentication/me/')
      this.pk = user.pk
      this.username = user.username
      this.name = user.full_name
    },
  },
})
