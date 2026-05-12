<template>
    <div class="header">
      <h1>Smart Poultry</h1>

      <div class="navigation">
        <router-link to ="/">
            <button class="nav-btn">Dashboard</button>
        </router-link>
        <router-link to="/cam">
            <button class="nav-btn">Cam</button>
        </router-link>        
        <button @click="app.toggleTheme()" class="theme-btn">
              {{ app.isDark ? '🌙 Dark' : '☀️ Light' }}
        </button>
      </div>

      <div class="status-box">
        <div :class="app.isOnline ? 'status online' : 'status offline'">
          {{ app.isOnline ? '🟢 ONLINE' : '🔴 OFFLINE' }}
        </div>
        <div class="time-card">
          <h3>Server Time: {{ app.serverClock }}</h3>
          <h3>Uptime ESP32: {{ app.uptime }}</h3>
        </div>
      </div>

    </div>
</template>

<style scoped>
</style>

<script setup>
import '../assets/css/header.css'

import { useAppStore } from '../stores/app'


const app = useAppStore()

</script>