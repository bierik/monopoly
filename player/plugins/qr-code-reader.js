import { QrcodeStream } from 'vue-qrcode-reader'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.component('QrcodeStream', QrcodeStream)
})
