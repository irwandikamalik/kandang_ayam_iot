import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '../pages/Dashboard.vue'
import Cam from '../pages/Cam.vue'

const routes = [
  {
    path: '/',
    component: Dashboard
  },
  {
    path: '/cam',
    component: Cam
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router