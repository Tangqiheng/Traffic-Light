<template>
  <div class="dashboard">
    <h1>智能交通灯控制系统</h1>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>路口状态</span>
            </div>
          </template>
          <div class="status-content">
            <p>路口ID: {{ intersectionData.intersection_id || 'intersection_001' }}</p>
            <p>最后更新: {{ currentTime }}</p>
            <el-tag type="success">正常运行</el-tag>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>交通概况</span>
            </div>
          </template>
          <div class="status-content">
            <p>总车流量: {{ trafficData.totalVehicles }} 辆</p>
            <p>平均速度: {{ trafficData.averageSpeed }} km/h</p>
            <p>拥堵路段: {{ trafficData.congestionPoints }} 处</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
            </div>
          </template>
          <div class="status-content">
            <p>传感器: <el-tag type="success">{{ systemStatus.sensors }}</el-tag></p>
            <p>摄像头: <el-tag type="success">{{ systemStatus.cameras }}</el-tag></p>
            <p>通信模块: <el-tag type="success">{{ systemStatus.communication }}</el-tag></p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>信号灯状态</span>
            </div>
          </template>
          <div class="traffic-light-grid">
            <div class="lane" v-for="lane in lightStatuses" :key="lane.direction">
              <p>{{ lane.direction }}车道</p>
              <el-tag :type="lane.status === '绿灯' ? 'success' : (lane.status === '黄灯' ? 'warning' : 'danger')">
                {{ lane.status }}
              </el-tag>
              <p>剩余时间: {{ lane.remainingTime }}s</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 32px; margin-bottom: 32px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header" style="display:flex;align-items:center;justify-content:space-between;">
              <span>实时交通统计表</span>
              <el-button size="small" type="danger" @click="onResetChart" plain>重置统计曲线</el-button>
            </div>
          </template>
          <div id="overviewChart" style="height:480px; background: linear-gradient(135deg, #f8fbff 0%, #eaf3fa 100%); border-radius: 18px; box-shadow: 0 4px 24px 0 rgba(64,158,255,0.08); padding: 16px;"></div>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>

import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
import api from '../services/api.js'
import * as echarts from 'echarts'

let initialized = false // 防止重复初始化

// 统计图相关
const statistics = ref({ points: [] })
let chart = null
let statisticsTimer = null
// 采样点持久化key
const STORAGE_KEY = 'dashboard_chart_data_v1'
let chartData = {
  times: [], // x轴时间（采样秒数）
  totalVehicles: [],
  avgSpeeds: []
}
// 加载本地采样点
function loadChartData() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed.times) && Array.isArray(parsed.totalVehicles) && Array.isArray(parsed.avgSpeeds)) {
        chartData.times = parsed.times
        chartData.totalVehicles = parsed.totalVehicles
        chartData.avgSpeeds = parsed.avgSpeeds
      }
    }
  } catch {}
}
// 保存采样点到本地
function saveChartData() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(chartData))
}
// 获取统计数据并渲染图表

// 实时数据推进，模拟/对接后端接口
// 采样点最大数量
const MAX_POINTS = 20
// 采样函数：每3秒采样一次，x轴为“系统运行/页面加载后起，精确到秒”
function fetchStatistics() {
  const now = new Date()
  // 采样时间点格式：HH:mm:ss
  function formatTime(date) {
    const pad = n => n.toString().padStart(2, '0')
    return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  }
  // 推入新采样点
  chartData.times.push(formatTime(now))
  chartData.totalVehicles.push(
    30 + Math.floor(Math.sin(chartData.times.length / 3) * 10) + Math.floor(Math.random() * 5)
  )
  chartData.avgSpeeds.push(
    35 + Math.floor(Math.cos(chartData.times.length / 4) * 6) + Math.floor(Math.random() * 3)
  )
  // 保持最大点数
  if (chartData.times.length > MAX_POINTS) {
    chartData.times.shift()
    chartData.totalVehicles.shift()
    chartData.avgSpeeds.shift()
  }
  saveChartData()
  // 联动更新交通概况
  trafficData.value.totalVehicles = chartData.totalVehicles[chartData.totalVehicles.length - 1]
  trafficData.value.averageSpeed = chartData.avgSpeeds[chartData.avgSpeeds.length - 1]
  renderChart()
}

function renderChart() {
  const dom = document.getElementById('overviewChart')
  if (!dom) return
  if (!chart) chart = echarts.init(dom)
  chart.setOption({
    backgroundColor: '#f8fafc',
    title: {
      text: '实时交通数据统计',
      left: 'center',
      top: 18,
      textStyle: {
        color: '#222',
        fontWeight: 600,
        fontSize: 18,
        fontFamily: 'Segoe UI, Arial, sans-serif',
        letterSpacing: 1
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      textStyle: { color: '#222', fontSize: 14, fontFamily: 'Segoe UI, Arial, sans-serif' },
      padding: 12,
      extraCssText: 'box-shadow:0 2px 12px rgba(0,0,0,0.06); border-radius:8px;'
    },
    legend: {
      data: ['总车流量', '平均速度'],
      top: 48,
      left: 'center',
      orient: 'horizontal',
      itemWidth: 32,
      itemHeight: 6,
      itemGap: 36,
      textStyle: { color: '#444', fontWeight: 500, fontSize: 15, fontFamily: 'Segoe UI, Arial, sans-serif' },
      icon: 'rect',
      // 只保留纯文字，去除所有富文本标记
      formatter: function(name) {
        return name;
      },
    },
    grid: {
      left: '5%',
      right: '5%',
      top: 64,
      bottom: 36,
      containLabel: true,
      borderRadius: 12
    },
    xAxis: {
      type: 'category',
      data: chartData.times,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#e5e7eb', width: 1 } },
      axisTick: { show: false },
      axisLabel: {
        color: '#888',
        fontWeight: 400,
        fontSize: 13,
        fontFamily: 'Segoe UI, Arial, sans-serif',
        formatter: function (value) {
          return value.slice(0, 12)
        }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '车流量(辆)',
        nameTextStyle: { color: '#3b82f6', fontWeight: 500, fontSize: 13, fontFamily: 'Segoe UI, Arial, sans-serif' },
        min: function (value) { return Math.max(0, value.min - 10) },
        max: function (value) { return value.max + 10 },
        position: 'left',
        axisLine: { show: false },
        axisLabel: { color: '#888', fontWeight: 400, fontSize: 13, fontFamily: 'Segoe UI, Arial, sans-serif' },
        splitLine: { show: true, lineStyle: { color: '#e5e7eb', type: 'dashed' } }
      },
      {
        type: 'value',
        name: '速度(km/h)',
        nameTextStyle: { color: '#22c55e', fontWeight: 500, fontSize: 13, fontFamily: 'Segoe UI, Arial, sans-serif' },
        min: function (value) { return Math.max(0, value.min - 5) },
        max: function (value) { return value.max + 5 },
        position: 'right',
        axisLine: { show: false },
        axisLabel: { color: '#bbb', fontWeight: 400, fontSize: 13, fontFamily: 'Segoe UI, Arial, sans-serif' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '总车流量',
        type: 'line',
        yAxisIndex: 0,
        data: chartData.totalVehicles,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#3b82f6', width: 2, cap: 'round' },
        itemStyle: { color: '#3b82f6', borderColor: '#fff', borderWidth: 1 },
        emphasis: { focus: 'series' }
      },
      {
        name: '平均速度',
        type: 'line',
        yAxisIndex: 1,
        data: chartData.avgSpeeds,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#22c55e', width: 2, cap: 'round' },
        itemStyle: { color: '#22c55e', borderColor: '#fff', borderWidth: 1 },
        emphasis: { focus: 'series' }
      }
    ],
    animation: true
  })
}


// 初始数据定义
const initialTrafficData = () => ({
  totalVehicles: 35,
  averageSpeed: 36.1,
  congestionPoints: 0
})
const initialIntersectionData = () => ({})
const initialSystemStatus = () => ({
  sensors: '在线',
  cameras: '在线',
  communication: '在线'
})
const initialLightStatuses = () => ([
  { direction: '北向', status: '绿灯', remainingTime: 13 },
  { direction: '东向', status: '红灯', remainingTime: 18 },
  { direction: '西向', status: '红灯', remainingTime: 13 },
  { direction: '南向', status: '绿灯', remainingTime: 18 }
])

const trafficData = ref(initialTrafficData())
const intersectionData = ref(initialIntersectionData())
const systemStatus = ref(initialSystemStatus())
const lightStatuses = ref(initialLightStatuses())
const currentTime = ref('')

let timer = null
let countdownTimer = null

function resetDashboardData() {
  // 重置所有响应式数据
  trafficData.value = initialTrafficData()
  intersectionData.value = initialIntersectionData()
  systemStatus.value = initialSystemStatus()
  lightStatuses.value = initialLightStatuses()
  currentTime.value = ''
  chartData.times = []
  chartData.totalVehicles = []
  chartData.avgSpeeds = []
  saveChartData()
  // 清理定时器
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

function updateCurrentTime() {
  currentTime.value = new Date().toLocaleString()
}

async function fetchTrafficData() {
  try {
    const response = await api.getTrafficStatus()
    if (response && response.data && response.data.length > 0) {
      const data = response.data[0]
      // 更新交通概况数据
      trafficData.value = {
        totalVehicles: data.vehicle_count || 35,
        averageSpeed: data.average_speed || 36.1,
        congestionPoints: data.congestion_level === '拥堵' ? 1 : 0
      }
      intersectionData.value = {
        intersection_id: data.intersection_id || 'intersection_001'
      }
      // 优先使用后端lights字段
      if (data.lights) {
        lightStatuses.value = [
          { direction: '北向', status: data.lights.north.status, remainingTime: data.lights.north.countdown },
          { direction: '东向', status: data.lights.east.status, remainingTime: data.lights.east.countdown },
          { direction: '西向', status: data.lights.west.status, remainingTime: data.lights.west.countdown },
          { direction: '南向', status: data.lights.south.status, remainingTime: data.lights.south.countdown }
        ]
      } else {
        // 兼容旧数据结构
        lightStatuses.value = [
          { direction: '北向', status: data.light_status || '绿灯', remainingTime: data.remaining_time || 13 },
          { direction: '东向', status: data.light_status === '绿灯' ? '红灯' : '绿灯', remainingTime: data.remaining_time || 18 },
          { direction: '西向', status: data.light_status === '绿灯' ? '红灯' : '绿灯', remainingTime: data.remaining_time || 13 },
          { direction: '南向', status: data.light_status === '绿灯' ? '绿灯' : '红灯', remainingTime: data.remaining_time || 18 }
        ]
      }
    } else {
      console.warn('交通数据为空或格式不正确')
    }
  } catch (error) {
    console.error('获取交通数据失败:', error)
    trafficData.value = {
      totalVehicles: 35,
      averageSpeed: 36.1,
      congestionPoints: 0
    }
    lightStatuses.value = [
      { direction: '北向', status: '绿灯', remainingTime: 13 },
      { direction: '东向', status: '红灯', remainingTime: 18 },
      { direction: '西向', status: '红灯', remainingTime: 13 },
      { direction: '南向', status: '绿灯', remainingTime: 18 }
    ]
  }
}





onMounted(() => {
  if (!initialized) {
    loadChartData()
    initialized = true
  }
  updateCurrentTime()
  timer = setInterval(updateCurrentTime, 1000)
  // 本地倒计时每秒跳动
  countdownTimer = setInterval(() => {
    lightStatuses.value.forEach(lane => {
      if (lane.remainingTime > 0) lane.remainingTime--
    })
  }, 1000)
  // 交通数据每3秒刷新
  fetchTrafficData()
  if (!window._trafficDataTimer) {
    window._trafficDataTimer = setInterval(fetchTrafficData, 3000)
  }
  renderChart()
  if (!statisticsTimer) {
    statisticsTimer = setInterval(fetchStatistics, 3000)
  }
})



onUnmounted(() => {
  // 不再重置数据，只清理定时器和图表实例，保证keep-alive缓存
  if (window._trafficDataTimer) {
    clearInterval(window._trafficDataTimer)
    window._trafficDataTimer = null
  }
  if (statisticsTimer) {
    clearInterval(statisticsTimer)
    statisticsTimer = null
  }
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.card-header {
  font-weight: bold;
}

.status-content p {
  margin: 10px 0;
}

.traffic-light-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 20px;
}

.lane {
  border: 1px solid #f0f0f0;
  padding: 16px;
  border-radius: 6px;
  background-color: #fff;
  text-align: center;
}

.lane p {
  margin: 8px 0;
}

.el-tag {
  margin: 0 4px;
}
</style>