<template>

  <div class="actuator-page">

    <!-- HEADER -->
    <div class="page-header">

      <h1>Actuator History</h1>

      <button
        class="refresh-btn"
        @click="loadHistory"
      >
        🔄 Refresh
      </button>

    </div>

    <!-- TABLE -->
    <div class="table-container">

      <table>

        <thead>

          <tr>

            <th>ID</th>

            <th>Fan</th>
            <th>Drink</th>
            <th>Lamp</th>
            <th>Feed</th>
            <th>Mode</th>

            <th>Suhu</th>
            <th>Humidity</th>
            <th>Gas</th>
            <th>Water</th>

            <th>Timestamp</th>

          </tr>

        </thead>

        <tbody>

          <tr
            v-for="item in history"
            :key="item.id"
          >

            <td>{{ item.id }}</td>

            <!-- FAN -->
            <td>
              <span :class="item.fan ? 'on' : 'off'">
                {{ item.fan ? 'ON' : 'OFF' }}
              </span>
            </td>

            <!-- DRINK -->
            <td>
              <span :class="item.drink ? 'on' : 'off'">
                {{ item.drink ? 'ON' : 'OFF' }}
              </span>
            </td>

            <!-- LAMP -->
            <td>
              <span :class="item.lamp ? 'on' : 'off'">
                {{ item.lamp ? 'ON' : 'OFF' }}
              </span>
            </td>

            <!-- FEED -->
            <td>
              <span :class="item.feed ? 'on' : 'off'">
                {{ item.feed ? 'ON' : 'OFF' }}
              </span>
            </td>

            <!-- AUTO -->
            <td>
              <span
                :class="
                  item.auto_mode
                  ? 'auto'
                  : 'manual'
                "
              >
                {{
                  item.auto_mode
                  ? 'AUTO'
                  : 'MANUAL'
                }}
              </span>
            </td>

            <!-- SENSOR -->
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

            <!-- TIME -->
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

const history = ref([])

const loadHistory = async () => {

  try {

    const res = await axios.get(
      `${API}/api/actuator-history`
    )

    history.value = res.data

  } catch (err) {

    console.error(
      'History error:',
      err
    )
  }
}

const formatDate = (date) => {

  const parts = date.split(' ')

  return `${parts[1]} ${parts[2]} ${parts[3]} ${parts[4]}`
}

onMounted(() => {

  loadHistory()

  setInterval(loadHistory, 3000)
})

</script>

<style scoped>

.actuator-page {

  min-height: 100vh;

  padding: 24px;

  box-sizing: border-box;
}


/* HEADER */
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


/* BUTTON */
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


/* TABLE */
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


/* LIGHT MODE */
body.light-mode .table-container {

  background: rgba(255,255,255,0.85);

  border: 1px solid rgba(0,0,0,0.08);

  box-shadow:
    0 8px 24px rgba(0,0,0,0.08);
}


/* TABLE */
table {

  width: 100%;

  border-collapse: collapse;

  min-width: 1200px;
}


/* HEADER TABLE */
thead {

  background: rgba(56,189,248,0.12);
}


/* CELL */
th,
td {

  padding: 14px;

  text-align: center;

  border-bottom:
    1px solid rgba(255,255,255,0.08);
}


/* LIGHT MODE CELL */
body.light-mode th,
body.light-mode td {

  border-bottom:
    1px solid rgba(0,0,0,0.08);
}


/* HEADER TEXT */
th {

  font-size: 15px;

  font-weight: 700;
}


/* ROW HOVER */
tbody tr {

  transition: 0.2s;
}

tbody tr:hover {

  background: rgba(56,189,248,0.08);
}


/* STATUS */
.on {

  color: #22c55e;

  font-weight: 700;
}

.off {

  color: #ef4444;

  font-weight: 700;
}


/* AUTO MODE */
.auto {

  color: #38bdf8;

  font-weight: 700;
}

.manual {

  color: #f59e0b;

  font-weight: 700;
}


/* MOBILE */
@media (max-width: 768px) {

  .actuator-page {

    padding: 14px;
  }

  th,
  td {

    padding: 10px;

    font-size: 13px;
  }
}

</style>