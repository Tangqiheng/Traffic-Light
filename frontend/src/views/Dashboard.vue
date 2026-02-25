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
            <div class="card-header">
              <span>实时交通统计表</span>
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

// 统计图相关
const statistics = ref({ points: [] })
let chart = null
let statisticsTimer = null
let chartData = {
  times: [], // x轴时间
  totalVehicles: [],
  avgSpeeds: []
}
// 获取统计数据并渲染图表

// 实时数据推进，模拟/对接后端接口
async function fetchStatistics() {
  try {
    // 假设后端返回最新一条数据点 {time, total_vehicles, average_speed}
    const r = await api.getTrafficStatistics ? await api.getTrafficStatistics() : { data: { points: [] } }
    // 兼容旧结构
    let newPoint = null
    if (r.data && Array.isArray(r.data.points) && r.data.points.length > 0) {
      newPoint = r.data.points[r.data.points.length - 1]
    } else if (r.data && Array.isArray(r.data.hourly_distribution) && r.data.hourly_distribution.length > 0) {
      // 兼容旧接口
      const last = r.data.hourly_distribution[r.data.hourly_distribution.length - 1]
      newPoint = {
        time: last.time || `${last.hour}:00`,
        total_vehicles: last.total_vehicles || last.average_vehicles || 0,
        average_speed: last.average_speed || 0
      }
    } else {
      // 模拟数据
      const now = new Date()
      newPoint = {
        time: now.toLocaleTimeString('zh-CN', { hour12: false }) + ' ' + String(now.getMilliseconds()).padStart(3, '0'),
        total_vehicles: Math.floor(Math.random() * 100),
        average_speed: Math.floor(Math.random() * 40) + 10
      }
    }
    // 推入数据，最多保留20个点
    chartData.times.push(newPoint.time)
    chartData.totalVehicles.push(newPoint.total_vehicles)
    chartData.avgSpeeds.push(newPoint.average_speed)
    if (chartData.times.length > 20) {
      chartData.times.shift()
      chartData.totalVehicles.shift()
      chartData.avgSpeeds.shift()
    }
    // 联动更新交通概况
    trafficData.value.totalVehicles = newPoint.total_vehicles
    trafficData.value.averageSpeed = newPoint.average_speed
    renderChart()
  } catch (e) {
    console.error('获取统计失败', e)
  }
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
        nameTextStyle: { color: '#888', fontWeight: 500, fontSize: 13, fontFamily: 'Segoe UI, Arial, sans-serif' },
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
        nameTextStyle: { color: '#888', fontWeight: 500, fontSize: 13, fontFamily: 'Segoe UI, Arial, sans-serif' },
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
// let dataTimer = null

function resetDashboardData() {
  // 重置所有响应式数据
  trafficData.value = initialTrafficData()
  intersectionData.value = initialIntersectionData()
  systemStatus.value = initialSystemStatus()
  lightStatuses.value = initialLightStatuses()
  currentTime.value = ''
  // 清理定时器
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  // 已去除 dataTimer
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
  resetDashboardData()
  updateCurrentTime()
  timer = setInterval(updateCurrentTime, 1000)
  // 只用统计图定时器，数据联动
  fetchStatistics()
  statisticsTimer = setInterval(fetchStatistics, 3000)
})

onUnmounted(() => {
  resetDashboardData()
  if (statisticsTimer) {
    clearInterval(statisticsTimer)
    statisticsTimer = null
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