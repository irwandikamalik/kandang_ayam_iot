import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '../pages/Dashboard.vue'
import Cam from '../pages/Cam.vue'
import Data from '../pages/Data.vue'
import Images from '../pages/Images.vue'
import Aktuator from '../pages/Aktuator.vue'

const routes = [
  {
    path: '/',
    component: Dashboard
  },
  {
    path: '/cam',
    component: Cam
  },
  {
    path: '/data',
    component: Data
  },
  {
    path: '/images',
    component: Images
  },
  {
    path: '/Aktuator',
    component: Aktuator
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router