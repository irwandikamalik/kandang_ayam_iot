import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAppStore } from './stores/app'
import './assets/css/theme.css'


import './style.css'

const app = createApp(App)

const pinia = createPinia()

createApp(App)
    .use(router)
    .use(pinia)
    .mount('#app')
