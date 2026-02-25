<template>
  <div class="monitor-page">
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in summaryCards" :key="card.key">
        <el-card class="summary-card">
          <div class="card-content">
            <div class="card-title">{{ card.title }}</div>
            <div class="card-value">{{ card.value }}</div>
            <div class="card-sub">{{ card.sub }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display:flex;align-items:center;justify-content:space-between">
              <span>路口实时车道状态</span>
              <el-button size="small" type="primary" @click="fetchTrafficStatus">刷新</el-button>
            </div>
          </template>
          <el-table :data="lanes" stripe style="width:100%">
            <el-table-column prop="id" label="车道ID" width="160" />
            <el-table-column prop="direction" label="方向" width="100" />
            <el-table-column prop="vehicle_count" label="车流量" width="100" />
            <el-table-column prop="average_speed" label="平均速度 (km/h)" width="160" />
            <el-table-column prop="queue_length" label="排队长度" width="120" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status === 'congested' ? 'danger' : (row.status === 'light' ? 'warning' : 'success')">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div>交通统计（最近24小时）</div>
          </template>
          <div id="overviewChart" style="height:320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card>
          <template #header>信号灯阶段</template>
          <el-timeline>
            <el-timeline-item v-for="phase in localPhases" :key="phase.id">
              <div style="display:flex;justify-content:space-between">
                <div>{{ phase.id }} — {{ phase.state }}</div>
                <div>剩余: {{ phase.remaining_time }}s</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>系统状态</template>
          <div style="padding:10px 0">
            <p>服务状态: <strong>{{ system.status }}</strong></p>
            <p>版本: <strong>{{ system.version }}</strong></p>
            <p>数据库: <strong>{{ system.services.database }}</strong></p>
            <p>MQTT: <strong>{{ system.services.mqtt }}</strong></p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '../services/api.js'

const lanes = ref([])
const overview = ref({ total_vehicles: 0, average_speed: 0, congestion_points: 0 })
const light = ref({ phases: [] })
const localPhases = ref([])
let lightCountdownTimer = null
const system = ref({ status: 'unknown', version: '-', services: {} })
const statistics = ref({ hourly_distribution: [] })

const summaryCards = ref([
  { key: 'total', title: '总车流量', value: 0, sub: '当前路口' },
  { key: 'speed', title: '平均速度', value: '0 km/h', sub: '实时平均' },
  { key: 'congestion', title: '拥堵点数', value: 0, sub: '异常车道数' },
  { key: 'service', title: '服务状态', value: 'unknown', sub: '系统总体' }
])

const fetchTrafficStatus = async () => {
  try {
    const r = await api.getTrafficStatus(intersectionId)
    const data = r.data
    lanes.value = data.lanes || []
  } catch (e) {
    console.error('获取车道状态失败', e)
  }
}

const fetchLightStatus = async () => {
  try {
    const r = await api.getTrafficLightStatus(intersectionId)
    light.value = r.data
    // 重置本地倒计时
    if (Array.isArray(light.value.phases)) {
      localPhases.value = light.value.phases.map(phase => ({ ...phase }))
    }
  } catch (e) {
    console.error('获取信号灯状态失败', e)
  }
}

const startLightCountdown = () => {
  if (lightCountdownTimer) clearInterval(lightCountdownTimer)
  lightCountdownTimer = setInterval(() => {
    if (Array.isArray(localPhases.value)) {
      localPhases.value = localPhases.value.map(phase => {
        if (phase.remaining_time > 0) {
          return { ...phase, remaining_time: phase.remaining_time - 1 }
        }
        return phase
      })
    }
  }, 1000)
}

const fetchOverview = async () => {
  try {
    const r = await api.getTrafficOverview ? await api.getTrafficOverview(intersectionId) : await api.getTrafficStatus(intersectionId)
    overview.value = r.data || r
    summaryCards.value[0].value = overview.value.total_vehicles || 0
    summaryCards.value[1].value = (overview.value.average_speed ? overview.value.average_speed + ' km/h' : '0 km/h')
    summaryCards.value[2].value = overview.value.congestion_points || 0
  } catch (e) {
    console.error('获取概览失败', e)
  }
}

const fetchStatistics = async () => {
  try {
    const r = await api.getTrafficStatistics()
    statistics.value = r.data || {}
    renderChart()
  } catch (e) {
    console.error('获取统计失败', e)
  }
}

const fetchSystemStatus = async () => {
  try {
    const r = await api.getSystemStatus()
    system.value = r.data || r
    summaryCards.value[3].value = system.value.status || 'unknown'
  } catch (e) {
    console.error('获取系统状态失败', e)
  }
}

const renderChart = () => {
  const dom = document.getElementById('overviewChart')
  if (!dom) return
  if (!chart) chart = echarts.init(dom)

  const hours = (statistics.value.hourly_distribution || []).map(i => `${i.hour}:00`)
  const values = (statistics.value.hourly_distribution || []).map(i => i.average_vehicles)

  chart.setOption({
    title: { text: '24小时车流量分布', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: hours.length ? hours : ['0:00','4:00','8:00','12:00','16:00','20:00'] },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: values.length ? values : [10,20,30,15,25,10], itemStyle: { color: '#409EFF' } }]
  })
}

onMounted(async () => {
  await fetchTrafficStatus()
  await fetchLightStatus()
  await fetchOverview()
  await fetchStatistics()
  await fetchSystemStatus()

  startLightCountdown()

  // 轮询实时数据
  pollTimer = setInterval(async () => {
    await fetchTrafficStatus()
    await fetchLightStatus()
    await fetchOverview()
    // 每次刷新信号灯状态后重置倒计时
    startLightCountdown()
  }, 10000)

  statsTimer = setInterval(fetchStatistics, 30000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (statsTimer) clearInterval(statsTimer)
  if (lightCountdownTimer) clearInterval(lightCountdownTimer)
  if (chart) chart.dispose()
})
</script>

<style scoped>
.monitor-page { padding: 20px }
.summary-card { text-align: left }
.card-content { padding: 10px }
.card-title { font-size: 14px; color: #666 }
.card-value { font-size: 22px; margin-top: 6px; font-weight: 700 }
.card-sub { margin-top: 6px; color: #999 }
</style>
