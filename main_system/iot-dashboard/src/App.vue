<template>

  <Header />

  <router-view />

</template>

<script setup>
import Header from './components/Header.vue'
import { onMounted, computed, ref, watch }
from 'vue'

import axios from 'axios'

import { useAppStore }
from './stores/app'

const API = window.location.origin
const app = useAppStore()

const realtime = ref({})
const serverTime = ref(0)

async function loadGlobal() {

  try {

    const res =
      await axios.get(`${API}/all`)

    const data = res.data

    realtime.value =
      data.realtime || {}

    serverTime.value =
      data.server_time || 0

    app.isOnline =
      isOnline.value

    app.uptime =
      uptime.value

    app.serverClock =
      serverClock.value

  } catch {

    app.isOnline = false
  }
}

const isOnline = computed(() => {

  if (!realtime.value.uptime)
    return false

  const now =
    Date.now() / 1000

  return (
    now -
    realtime.value.last_update
  ) < 5
})

const uptime = computed(() => {

  const sec =
    realtime.value.uptime || 0

  const h =
    Math.floor(sec / 3600)

  const m =
    Math.floor((sec % 3600) / 60)

  const s = sec % 60

  return `${h}h ${m}m ${s}s`
})

const serverClock = computed(() => {

  const date =
    new Date(
      serverTime.value * 1000
    )

  return date.toLocaleTimeString()
})

onMounted(() => {

  if (!app.isDark) {

    document.body.classList.add(
      'light-mode'
    )
  }

  loadGlobal()

  setInterval(
    loadGlobal,
    1000
  )
})

watch(() => app.isDark, (val) => {

  localStorage.setItem(
    'theme',
    val ? 'dark' : 'light'
  )

  document.body.classList.toggle(
    'light-mode',
    !val
  )
})
</script>
