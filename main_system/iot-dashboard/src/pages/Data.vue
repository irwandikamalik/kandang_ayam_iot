<template>

  <div class="data-page">

    <div class="page-header">
      <h1>Sensor Data</h1>
      <button
        class="refresh-btn"
        @click="loadData"
      >
        🔄 Refresh
      </button>
    </div>

    <div class="table-container">

      <table>

        <thead>
          <tr>
            <th>ID</th>
            <th>Suhu</th>
            <th>Humidity</th>
            <th>Gas</th>
            <th>Water</th>
            <th>Created At</th>
          </tr>
        </thead>

        <tbody>

          <tr
            v-for="item in sensorData"
            :key="item.id"
          >
            <td>{{ item.id }}</td>

            <td>
              {{ Number(item.suhu).toFixed(2) }} °C
            </td>

            <td>
              {{ Number(item.humidity).toFixed(2) }} %
            </td>

            <td>
              {{ Number(item.gas).toFixed(2) }} ppm
            </td>

            <td>
              {{ Number(item.water).toFixed(2) }} %
            </td>

            <td>
              {{ formatDate(item.created_at) }}
            </td>
          </tr>

        </tbody>

      </table>

    </div>

  </div>

</template>

<script setup>

import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = window.location.origin

const sensorData = ref([])

const loadData = async () => {

  try {

    const res = await axios.get(
      `${API}/api/data`
    )

    sensorData.value = res.data

  } catch (err) {

    console.error(
      'Load data error:',
      err
    )
  }
}

const formatDate = (date) => {

  const parts = date.split(' ')

  return `${parts[1]} ${parts[2]} ${parts[3]} ${parts[4]}`
}

onMounted(() => {

  loadData()

  setInterval(loadData, 5000)
})

</script>

<style scoped>

.data-page {

  min-height: 100vh;

  padding: 24px;

  box-sizing: border-box;
}

.page-header {

  display: flex;

  justify-content: space-between;

  align-items: center;

  margin-bottom: 24px;

  gap: 16px;

  flex-wrap: wrap;
}

.page-header h1 {

  margin: 0;

  font-size: clamp(28px, 5vw, 48px);

  font-weight: 800;

  background: linear-gradient(
    90deg,
    #38bdf8,
    #a78bfa
  );

  -webkit-background-clip: text;

  color: transparent;
}

.refresh-btn {

  border: none;

  padding: 12px 20px;

  border-radius: 14px;

  cursor: pointer;

  font-weight: 700;

  color: white;

  background: linear-gradient(
    135deg,
    #38bdf8,
    #a78bfa
  );

  transition: 0.2s;
}

.refresh-btn:hover {

  transform: translateY(-2px);
}

.refresh-btn:active {

  transform: scale(0.96);
}

.table-container {

  width: 100%;

  overflow-x: auto;

  border-radius: 24px;

  background: rgba(255,255,255,0.04);

  backdrop-filter: blur(12px);

  border: 1px solid rgba(255,255,255,0.08);

  box-shadow:
    0 10px 30px rgba(0,0,0,0.35);
}

body.light-mode .table-container {

  background: rgba(255,255,255,0.85);

  border: 1px solid rgba(0,0,0,0.08);

  box-shadow:
    0 8px 24px rgba(0,0,0,0.08);
}

table {

  width: 100%;

  border-collapse: collapse;

  min-width: 700px;
}

thead {

  background: rgba(56,189,248,0.12);
}

th,
td {

  padding: 14px;

  text-align: center;

  border-bottom:
    1px solid rgba(255,255,255,0.08);
}

body.light-mode th,
body.light-mode td {

  border-bottom:
    1px solid rgba(0,0,0,0.08);
}

th {

  font-size: 15px;

  font-weight: 700;
}

tbody tr {

  transition: 0.2s;
}

tbody tr:hover {

  background: rgba(56,189,248,0.08);
}

@media (max-width: 768px) {

  .data-page {

    padding: 14px;
  }

  th,
  td {

    padding: 10px;

    font-size: 13px;
  }
}

</style>