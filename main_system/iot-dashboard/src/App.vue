<template>
  <div class="dashboard">

    <!-- HEADER -->
    <div class="header">
      <h1>🔥 IoT Dashboard</h1>
      
      <div :class="isOnline ? 'status online' : 'status offline'">
        {{ isOnline ? '🟢 ONLINE' : '🔴 OFFLINE' }}
      </div>

      <div class="time-card">
        <h3>Server Time</h3>
        <p>{{ serverClock }}</p>
      </div>

      <div class="time-card">
        <h3>Uptime ESP32</h3>
        <p>{{ uptime }}</p>
      </div>
    </div>

    <!-- SENSOR CARDS -->
    <div class="sensor-cards">
      <div class="card suhu">
        <FireIcon class="icon suhu-icon"/>
        <h3>Suhu</h3>
        <p>{{ suhu }}°C</p>
      </div>

      <div class="card hum">
        <CloudIcon class="icon hum-icon"/>
        <h3>Humidity</h3>
        <p>{{ humidity }}%</p>
      </div>

      <div class="card gas">
        <BeakerIcon class="icon gas-icon"/>
        <h3>Gas</h3>
        <p>{{ gas }} ppm</p>
      </div>
    </div>

    <!-- MAIN GRID -->
    <div class="main-grid">

      <!-- CONTROL -->
      <div class="panel">
        <h2>🎛️ Control</h2>

        <div class="control-item">
          <span class="control-label">
            <Fan class="mini-icon fan-icon"/>
            Fan
          </span>
          <input type="checkbox" v-model="fan" @change="toggleFan">
        </div>

        <div class="control-item">
          <span class="control-label">
            <Droplet class="mini-icon drink-icon"/>
            drink
          </span>
          <input type="checkbox" v-model="drink" @change="toggleDrink">
        </div>

        <div class="control-item">
          <span class="control-label">
            <LightBulbIcon class="mini-icon lamp-icon"/>
            Lamp
          </span>
          <input type="checkbox" v-model="lamp" @change="toggleLamp">
        </div>

        <div class="control-item">
          <span class="control-label">
            <CloudIcon class="mini-icon mist-icon"/>
            Mist
          </span>
          <input type="checkbox" v-model="mist" @change="toggleMist">
        </div>

        <div class="control-item">
          <span class="control-label">
            <SparklesIcon class="mini-icon auto-icon"/>
            Auto
          </span>
          <input type="checkbox" v-model="auto" @change="toggleAuto">
        </div>

        <button @click="feedNow" class="feed-btn">
          🍽️ Feed
        </button>

        <div class="panel">
          <h2>📌 Setpoint Aktif</h2>

          <div class="control-item">
            <span>Suhu</span>
            <b>{{ current_sp.suhu }}</b>
          </div>

          <div class="control-item">
            <span>Humidity</span>
            <b>{{ current_sp.hum }}</b>
          </div>

          <div class="control-item">
            <span>Gas</span>
            <b>{{ current_sp.gas }}</b>
          </div>
        </div>

        <div class="panel">
          <h2>✏️ Setpoint Baru</h2>

          <div class="control-item">
            <span>Suhu</span>
            <input type="number" v-model="sp_suhu">
          </div>

          <div class="control-item">
            <span>Humidity</span>
            <input type="number" v-model="sp_hum">
          </div>

          <div class="control-item">
            <span>Gas</span>
            <input type="number" v-model="sp_gas">
          </div>

          <button @click="saveSetpoint" class="feed-btn">
            💾 Save
          </button>
        </div>

      </div>

      <!-- CHART -->
      <div class="panel charts">
        <h2>📊 Monitoring</h2>

        <canvas id="chartSuhu"></canvas>
        <canvas id="chartHum"></canvas>
        <canvas id="chartGas"></canvas>
      </div>

    </div>
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  background: #0b1220;
  color: #e2e8f0;
}

/* LAYOUT */
.dashboard {
  max-width: 1200px;
  margin: auto;
  padding: 20px;
}

/* HEADER */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status {
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: bold;
}

.online {
  background: rgba(34,197,94,0.2);
  color: #22c55e;
}

.time-card{
  size: 50%;
}

.offline {
  background: rgba(239,68,68,0.2);
  color: #ef4444;
}

/* icon */
.control-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ICON BASE */
.mini-icon {
  width: 18px;
  transition: 0.3s;
}

.icon {
  width: 28px;
  margin-bottom: 5px;
}

.mini-icon {
  width: 18px;
  margin-right: 5px;
}

/* Data Icon */
.suhu-icon { color: #f97316;   transition: 0.3s; }
.hum-icon { color: #06b6d4; }
.gas-icon { color: #ef4444; }

/* Control Icon */
.fan-icon  { color: #38bdf8; }
.drink-icon { color: #60a5fa; }
.lamp-icon { color: #facc15; }
.mist-icon { color: #38bdf8; }
.auto-icon { color: #a78bfa; }

/* on State */
.control-item:has(input:checked) .fan-icon {
  animation: spin 1s linear infinite;
  color: #0ea5e9;
  filter: drop-shadow(0 0 6px #38bdf8);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.control-item:has(input:checked) .drink-icon {
  color: #3b82f6;
  filter: drop-shadow(0 0 6px #60a5fa);
}

.control-item:has(input:checked) .lamp-icon {
  filter: drop-shadow(0 0 10px #fde047);
}

.control-item:has(input:checked) .mist-icon {
  color: #0ea5e9;
  filter: drop-shadow(0 0 6px #38bdf8);
}

.control-item:has(input:checked) .auto-icon {
  color: #8b5cf6;
  filter: drop-shadow(0 0 6px #a78bfa);
}

/* BACKGROUND EFFECT SAAT AKTIF */
.control-item:has(input:checked) {
  background: rgba(255,255,255,0.05);
  padding: 6px 10px;
  border-radius: 8px;
  transition: 0.2s;
}

.card:hover {
  transform: translateY(-5px);
  transition: 0.2s;
}
/* SENSOR CARDS */
.sensor-cards {
  display: flex;
  gap: 15px;
  margin: 20px 0;
}

.card {
  flex: 1;
  padding: 20px;
  border-radius: 14px;
  text-align: center;
  background: #111827;
  box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}

.card h3 {
  margin: 0;
  color: #94a3b8;
}

.card p {
  font-size: 26px;
  font-weight: bold;
  margin-top: 10px;
}

/* warna beda tiap sensor */
.suhu { border-left: 5px solid #f97316; }
.hum  { border-left: 5px solid #06b6d4; }
.gas  { border-left: 5px solid #ef4444; }

/* GRID */
.main-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
}

/* PANEL */
.panel {
  background: #111827;
  padding: 20px;
  border-radius: 14px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}

/* CONTROL */
.control-item {
  display: flex;
  justify-content: space-between;
  margin: 15px 0;
}

/* SWITCH */
input[type="checkbox"] {
  width: 42px;
  height: 22px;
  appearance: none;
  background: #374151;
  border-radius: 20px;
  position: relative;
  cursor: pointer;
  transition: 0.3s;
}

input[type="checkbox"]:checked {
  background: #22c55e;
}

input[type="checkbox"]::before {
  content: "";
  width: 18px;
  height: 18px;
  background: white;
  position: absolute;
  top: 2px;
  left: 2px;
  border-radius: 50%;
  transition: 0.3s;
}

input[type="checkbox"]:checked::before {
  left: 22px;
}

/* BUTTON */
.feed-btn {
  margin-top: 20px;
  padding: 12px;
  width: 100%;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: 0.2s;
}

.feed-btn:hover {
  transform: scale(1.05);
}

/* CHART */
canvas {
  margin-top: 15px;
  background: #020617;
  padding: 10px;
  border-radius: 10px;
}

/* RESPONSIVE */
@media (max-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr;
  }

  .sensor-cards {
    flex-direction: column;
  }
}
</style>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'
import {
  FireIcon,
  CloudIcon,
  BeakerIcon,
  BoltIcon,
  LightBulbIcon,
  SparklesIcon,
  ArrowPathIcon 
} from '@heroicons/vue/24/solid'
import { Fan, Droplet, Sliders } from 'lucide-vue-next'


const API = 'http://192.168.100.82:5000'

const realStatus = ref({})

//Control State
const fan = ref(false)
const drink = ref(false)
const lamp = ref(false)
const mist = ref(false)
const auto = ref(false)
const serverTime = ref(0)
const realtime = ref({})

//Data Sensor
const suhu = ref(0)
const humidity = ref(0)
const gas = ref(0)

let chartSuhu, chartHum, chartGas
let lastId = null
let isFirstLoad = true
let isUpdating = false

const sp_suhu = ref(0)
const sp_hum = ref(0)
const sp_gas = ref(0)

const current_sp = ref({
  suhu: 0,
  hum: 0,
  gas: 0
})

const saveSetpoint = async () => {
  await axios.post(`${API}/setpoint`, {
    suhu: sp_suhu.value,
    hum: sp_hum.value,
    gas: sp_gas.value
  })

  // refresh setpoint aktif
  loadSetpoint()
}

const setpoint = async () => {
  await axios.post(`${API}/setpoint`, {
    suhu: 0,
    hum: 0,
    gas: 0
  })
}

const loadSetpoint = async () => {
  const res = await axios.get(`${API}/get-setpoint`)

  current_sp.value = res.data

  // isi default form (sekali aja kalau kosong)
  if (sp_suhu.value === 0) {
    sp_suhu.value = res.data.suhu
    sp_hum.value = res.data.hum
    sp_gas.value = res.data.gas
  }
}

// toggle function (Button)
const toggleFan = async () => {
  isUpdating = true

  await axios.post(`${API}/fan`, { state: fan.value })

  setTimeout(() => {
    isUpdating = false
  }, 800)
}

const toggleDrink = async () => {
  isUpdating = true

  await axios.post(`${API}/drink`, { state: drink.value })

  setTimeout(() => {
    isUpdating = false
  }, 800)
}

const toggleLamp = async () => {
  isUpdating = true

  await axios.post(`${API}/lamp`, { state: lamp.value })
  
  setTimeout(() => {
    isUpdating = false
  }, 800)
}

const toggleMist = async () => {
  isUpdating = true

  await axios.post(`${API}/mist`, { state: mist.value })
  
  setTimeout(() => {
    isUpdating = false
  }, 800)
}

const toggleAuto = async () => {
  isUpdating = true

  await axios.post(`${API}/auto`, { state: auto.value })

  setTimeout(() => {
    isUpdating = false
  }, 800)  
}

const feedNow = async () => {
  await axios.post(`${API}/feed`)
}


const createChart = (ctx, label, color) => {
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: label,
          data: [],
          borderColor: color,
          animation: false
        },
        {
          label: 'Setpoint',
          data: [],
          borderColor: 'white',
          borderDash: [5, 5], 
          animation: false
        }
      ]
    },
        options: {
      scales: {
        x: {
          ticks: {
            maxTicksLimit: 10,
            maxRotation: 0,   
            minRotation: 0,
            autoSkip: true
          }
        }
      }
    }

  })
}

const initChart = () => {
  chartSuhu = createChart(document.getElementById('chartSuhu'), 'Suhu', 'orange')
  chartHum = createChart(document.getElementById('chartHum'), 'Humidity', 'cyan')
  chartGas = createChart(document.getElementById('chartGas'), 'Gas', 'red')
}

const pushData = (chart, value, sp, time) => {

  if (chart.data.labels.length > 20) {
    chart.data.labels.shift()
    chart.data.datasets[0].data.shift()
    chart.data.datasets[1].data.shift()
  }

  chart.data.labels.push(time)
  chart.data.datasets[0].data.push(value)
  chart.data.datasets[1].data.push(sp)

  chart.options.scales = {
    x: {
      ticks: {
        maxTicksLimit: 10
      }
    }
  }

  chart.update()
}

const updateChart = (data) => {
  const time = new Date(data.created_at).toLocaleTimeString('id-ID', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })


  pushData(chartSuhu, data.suhu, current_sp.value.suhu, time)
  pushData(chartHum, data.humidity, current_sp.value.hum, time)
  pushData(chartGas, data.gas, current_sp.value.gas, time)
}

const loadAll = async () => {
  try {
    const res = await axios.get(`${API}/all`)
    const data = res.data
    serverTime.value = data.server_time || 0
    realtime.value = data.realtime || {}


    if (data.sensor.length === 0) return

    const sensor = data.sensor
    const latest = sensor[0]

    suhu.value = latest.suhu
    humidity.value = latest.humidity
    gas.value = latest.gas

    if (!isUpdating) {
      fan.value = data.status.fan ?? false
      drink.value = data.status.drink ?? false
      lamp.value = data.status.lamp ?? false
      mist.value = data.status.mist ?? false
      auto.value = data.status.auto ?? false
    }

    realStatus.value = data.status || {}

    if (isFirstLoad) {
      const reversed = sensor.slice(0, 20).reverse()

      reversed.forEach((d, i) => {
        let timeLabel = i % 2 === 0
          ? new Date(d.created_at).toLocaleTimeString()
          : ''

        chartSuhu.data.labels.push(timeLabel)
        chartSuhu.data.datasets[0].data.push(d.suhu)
        chartSuhu.data.datasets[1].data.push(current_sp.value.suhu)

        chartHum.data.labels.push(timeLabel)
        chartHum.data.datasets[0].data.push(d.humidity)
        chartHum.data.datasets[1].data.push(current_sp.value.hum)

        chartGas.data.labels.push(timeLabel)
        chartGas.data.datasets[0].data.push(d.gas)
        chartGas.data.datasets[1].data.push(current_sp.value.gas)
      })

      chartSuhu.update()
      chartHum.update()
      chartGas.update()

      lastId = latest.id
      isFirstLoad = false
      return
    }

    // ✅ pindahin ke dalam try
    if (latest.id === lastId) return
    lastId = latest.id

    updateChart(latest)

  } catch (err) {
    console.error("API error:", err)
  }
}


const isOnline = computed(() => {
  if (!realtime.value.uptime) return false

  const now = Date.now() / 1000

  // pakai waktu server terakhir update sensor
  return (now - realtime.value.last_update) < 5
})

const uptime = computed(() => {
  const sec = realtime.value.uptime || 0

  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60

  return `${h}h ${m}m ${s}s`
})

const serverClock = computed(() => {
  const date = new Date(serverTime.value * 1000)
  return date.toLocaleTimeString()
})

onMounted(() => {
  initChart()
  loadAll()
  loadSetpoint()
  setInterval(loadAll, 1000)
})
</script>