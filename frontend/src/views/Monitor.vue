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
  // 移除后端统计数据依赖
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
            <div>实时交通统计表</div>
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
// 实时统计曲线数据
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '../services/api.js'

const realtimeTimestamps = ref([]) // x轴时间点
const realtimeFlow = ref([])       // 总车流量
const realtimeSpeed = ref([])      // 平均速度
let realtimeTimer = null
const MAX_POINTS = 1200 // 最多保留1小时数据（3秒采样一次）

const lanes = ref([])
const overview = ref({ total_vehicles: 0, average_speed: 0, congestion_points: 0 })
const light = ref({ phases: [] })
const localPhases = ref([])
let lightCountdownTimer = null
let pollTimer = null
let statsTimer = null
let chart = null
const system = ref({ status: 'unknown', version: '-', services: {} })
// 移除后端统计数据依赖

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

// 移除fetchStatistics函数

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

  chart.setOption({
    title: { text: '实时交通统计表', left: 'center' },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: params => {
        let t = params[0]?.axisValue || ''
        let flow = params.find(p => p.seriesName === '总车流量')?.data ?? '-'
        let speed = params.find(p => p.seriesName === '平均速度')?.data ?? '-'
        return `${t}<br/>总车流量：<b>${flow}</b><br/>平均速度：<b>${speed}</b>`
      }
    },
    legend: { data: ['总车流量', '平均速度'] },
    xAxis: {
      type: 'category',
      data: realtimeTimestamps.value,
      axisLabel: {
        formatter: v => v,
        rotate: 30,
        showMaxLabel: true,
        showMinLabel: true,
        interval: 0 // 强制显示每个点的label
      },
      boundaryGap: false,
      splitNumber: realtimeTimestamps.value.length,
      min: 'dataMin',
      max: 'dataMax',
    },
    yAxis: [
      { type: 'value', name: '车流量(辆)', minInterval: 1 },
      { type: 'value', name: '速度(km/h)', min: 0, max: 120, position: 'right' }
    ],
    series: [
      {
        name: '总车流量',
        type: 'line',
        data: realtimeFlow.value,
        yAxisIndex: 0,
        smooth: true,
        showSymbol: true,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '平均速度',
        type: 'line',
        data: realtimeSpeed.value,
        yAxisIndex: 1,
        smooth: true,
        showSymbol: true,
        itemStyle: { color: '#67C23A' }
      }
    ]
  })
}

onMounted(async () => {
    // 页面加载时强制清空采样数据，彻底避免历史/缓存影响
    realtimeTimestamps.value = []
    realtimeFlow.value = []
    realtimeSpeed.value = []
    // 实时采样定时器（每3秒采样一次总车流量和平均速度）
    const pushRealtimePoint = () => {
      const now = new Date()
      // 记录精确到秒的真实时间（YYYY-MM-DD HH:mm:ss）
      const pad = n => n.toString().padStart(2, '0')
      const timeStr = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
      realtimeTimestamps.value.push(timeStr)
      realtimeFlow.value.push(overview.value.total_vehicles || 0)
      realtimeSpeed.value.push(overview.value.average_speed || 0)
      if (realtimeTimestamps.value.length > MAX_POINTS) {
        realtimeTimestamps.value.shift()
        realtimeFlow.value.shift()
        realtimeSpeed.value.shift()
      }
      renderChart()
    }
  await fetchTrafficStatus()
  await fetchLightStatus()
  await fetchOverview()
  // 不再拉取后端统计数据
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

  // 不再定时拉取后端统计数据

  pushRealtimePoint() // 首次采样
  realtimeTimer = setInterval(pushRealtimePoint, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  // 不再定时拉取后端统计数据
  if (lightCountdownTimer) clearInterval(lightCountdownTimer)
  if (realtimeTimer) clearInterval(realtimeTimer)
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
