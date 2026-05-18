<template>
  <div class="dashboard">

    <!-- SENSOR CARDS -->
    <div class="sensor-cards">
      <div class="card suhu">
        <FireIcon class="icon suhu-icon"/>
        <h3>Suhu</h3>
        <p>{{ suhu.toFixed(2) }}°C</p>
        <h4>Setpoint: {{ current_sp.suhu }}</h4>
      </div>

      <div class="card hum">
        <CloudIcon class="icon hum-icon"/>
        <h3>Humidity</h3>
        <p>{{ humidity.toFixed(2) }}%</p>
        <h4>Setpoint: {{ current_sp.hum }}</h4>
      </div>

      <div class="card gas">
        <BeakerIcon class="icon gas-icon"/>
        <h3>Gas</h3>
        <p>{{ gas.toFixed(2) }} ppm</p>
        <h4>Setpoint: {{ current_sp.gas }}</h4>
      </div>
      
      <div class="card water">
        <Droplet  class="icon water-icon"/>
        <h3>Water</h3>
        <p>{{ water.toFixed(2) }} %</p>
        <h4>Setpoint: {{ current_sp.water }}</h4>
      </div>
    </div>

    <!-- CONTROL -->
    <div class="control-box">
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
          <SparklesIcon class="mini-icon auto-icon"/>
          Auto
        </span>
        <input type="checkbox" v-model="auto" @change="toggleAuto">
      </div>

      <button
        @click="feedNow"
        class="feed-btn"
        :class="{ feeding: feed }"
      >
        {{
          feed
          ? '🍽️ Feeding...'
          : '🍽️ Feed'
        }}
      </button>
    </div>  
        

    <div class="setpoint-box">
      <div class="setpoint-item">
        <span>Suhu</span>
        <input type="number" v-model="sp_suhu">
      </div>

      <div class="setpoint-item">
        <span>Humidity</span>
        <input type="number" v-model="sp_hum">
      </div>

      <div class="setpoint-item">
        <span>Gas</span>
        <input type="number" v-model="sp_gas">
      </div>
      
      <div class="setpoint-item">
        <span>Water</span>
        <input type="number" v-model="sp_water">
      </div>

      <button @click="saveSetpoint" class="feed-btn">
        💾 Save
      </button>
    </div>

      <!-- CHART -->
      <div class="panel charts">
        <h2 class="monitor-title">
          <ChartBarIcon class="icon chart-icon"/>
          Grafik
        </h2>
        <div class="chart-wrapper">
          <canvas id="chartSuhu"></canvas>
        </div>

        <div class="chart-wrapper">
          <canvas id="chartHum"></canvas>
        </div>

        <div class="chart-wrapper">
          <canvas id="chartGas"></canvas>
        </div>

        <div class="chart-wrapper">
          <canvas id="chartWater"></canvas>
        </div>      
      </div>
  </div>
</template>

<script setup>
import '../assets/css/Dashboard.css'

import Header from '../components/Header.vue'
import { useAppStore } from '../stores/app'

import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'
import {
  FireIcon,
  CloudIcon,
  BeakerIcon,
  BoltIcon,
  LightBulbIcon,
  SparklesIcon,
  ArrowPathIcon,
  ChartBarIcon
} from '@heroicons/vue/24/solid'
import { Fan, Droplet, Sliders, ChartBar } from 'lucide-vue-next'

const API = window.location.origin

const app = useAppStore()

const getChartTextColor = () => {

  return document.body.classList.contains(
    'light-mode'
  )

    ? '#000000'

    : '#ffffff'
}

const getChartGridColor = () => {

  return document.body.classList.contains(
    'light-mode'
  )

    ? 'rgba(0,0,0,0.08)'

    : 'rgba(255,255,255,0.08)'
}

const realStatus = ref({})
const serverTime = ref(0)
const realtime = ref({})

//Control State
const fan = ref(false)
const drink = ref(false)
const lamp = ref(false)
const auto = ref(false)


//Data Sensor
const suhu = ref(0)
const humidity = ref(0)
const gas = ref(0)
const water = ref(0)

let chartSuhu, chartHum, chartGas, chartWater
let lastId = null
let isFirstLoad = true
let isUpdating = false

const sp_suhu = ref(0)
const sp_hum = ref(0)
const sp_gas = ref(0)
const sp_water = ref(0)

const current_sp = ref({
  suhu: 0,
  hum: 0,
  gas: 0,
  water: 0
})

const saveSetpoint = async () => {
  await axios.post(`${API}/setpoint`, {
    suhu: sp_suhu.value,
    hum: sp_hum.value,
    gas: sp_gas.value,
    water: sp_water.value
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
    sp_gas.value = res.data.gas,
    sp_water.value = res.data.water
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

const chartFillColors = {

  orange: 'rgba(249,115,22,0.15)',

  cyan: 'rgba(6,182,212,0.15)',

  red: 'rgba(239,68,68,0.15)',

  blue: 'rgba(59,130,246,0.15)'
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

          borderWidth: 3,

          pointRadius: 2,

          pointHoverRadius: 6,

          tension: 0.35,

          fill: true,

          backgroundColor:
            chartFillColors[color],

          animation: {
            duration: 1
          }
        },

        {
          label: 'Setpoint',

          data: [],

          borderColor: '#a78bfa',

          borderDash: [5, 5],

          pointRadius: 0,

          borderWidth: 2,

          tension: 0
        }
      ]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 0,
      animation: false,
      layout: {

        padding: {

          top: 20,

          bottom: 20,

          left: 10,

          right: 10
        }
      },

      plugins: {

        legend: {

          labels: {

            color: getChartTextColor()
          }
        }
      },

      scales: {

        x: {

          border: {

            color: getChartGridColor(),

            width: 2
          },

          ticks: {

            color: getChartTextColor(),

            maxTicksLimit: 10,

            maxRotation: 0,

            minRotation: 0
          },

          grid: {

            color: getChartGridColor()
          }
        },

        y: {

          border: {

            color: getChartGridColor(),

            width: 2
          },

          ticks: {

            color: getChartTextColor(),

            padding: 10
          },

          grid: {

            color: getChartGridColor()
          },

          grace: '25%'
        }
      }
    }
  })
}

const initChart = () => {

  chartSuhu = createChart(document.getElementById('chartSuhu'), 'Suhu', 'orange')
  chartHum = createChart(document.getElementById('chartHum'), 'Humidity', 'cyan')
  chartGas = createChart(document.getElementById('chartGas'), 'Gas', 'red')
  chartWater = createChart(document.getElementById('chartWater'), 'Water', 'blue')
}

const updateSingleChart = (
  chart,
  sensorData,
  field,
  setpoint
) => {

  chart.data.labels = sensorData.map(item => {

    return item.created_at
      .split(' ')[4]

  }).reverse()

  chart.data.datasets[0].data = sensorData.map(
    item => item[field]
  ).reverse()

  chart.data.datasets[1].data = sensorData.map(
    () => setpoint
  ).reverse()

  chart.update()

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
    water.value = latest.water || 0

    if (!isUpdating) {
      fan.value = data.status.fan ?? false
      drink.value = data.status.drink ?? false
      lamp.value = data.status.lamp ?? false
      auto.value = data.status.auto ?? false
    }

    realStatus.value = data.status || {}

    if (isFirstLoad) {
      updateSingleChart(
        chartSuhu,
        sensor,
        'suhu',
        current_sp.value.suhu
      )

      updateSingleChart(
        chartHum,
        sensor,
        'humidity',
        current_sp.value.hum
      )

      updateSingleChart(
        chartGas,
        sensor,
        'gas',
        current_sp.value.gas
      )

      updateSingleChart(
        chartWater,
        sensor,
        'water',
        current_sp.value.water
      )

      lastId = latest.id

      isFirstLoad = false
      return
    }

    if (latest.id === lastId) return
    lastId = latest.id

    updateSingleChart(
      chartSuhu,
      sensor,
      'suhu',
      current_sp.value.suhu
    )

    updateSingleChart(
      chartHum,
      sensor,
      'humidity',
      current_sp.value.hum
    )

    updateSingleChart(
      chartGas,
      sensor,
      'gas',
      current_sp.value.gas
    )

    updateSingleChart(
      chartWater,
      sensor,
      'water',
      current_sp.value.water
    )

  } catch (err) {
    console.error("API error:", err)
  }
}


onMounted(() => {
  initChart()
  loadAll()
  loadSetpoint()
  setInterval(loadAll, 1000)
})

watch(() => app.isDark, () => {

  const charts = [

    chartSuhu,
    chartHum,
    chartGas,
    chartWater
  ]

  charts.forEach(chart => {

    chart.options.plugins.legend.labels.color =
      getChartTextColor()

    chart.options.scales.x.ticks.color =
      getChartTextColor()

    chart.options.scales.y.ticks.color =
      getChartTextColor()

    chart.options.scales.x.grid.color =
      getChartGridColor()

    chart.options.scales.y.grid.color =
      getChartGridColor()
  })
})

</script>