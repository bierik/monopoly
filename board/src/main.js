import { createApp } from 'vue'
import router from '@/router'
import './index.css'
import App from '@/App.vue'
import mqtt from '@/mqtt_client'

await mqtt.connect('mqtt://localhost:5001')

const app = createApp(App)
app.use(router)
app.mount('#app')
