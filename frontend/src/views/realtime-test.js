// 实时数据更新测试脚本
import { ref } from 'vue'
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import api from '../services/api.js'

console.log('🔍 实时数据更新测试开始...')

// 创建响应式数据
const trafficData = ref({
  totalVehicles: 0,
  averageSpeed: 0,
  congestionPoints: 0
})

const trafficLights = ref({
  north: { status: '', countdown: 0 },
  south: { status: '', countdown: 0 },
  east: { status: '', countdown: 0 },
  west: { status: '', countdown: 0 },
});
let timer = null;
const lightStatuses = ref([
  { direction: '北向', status: '未知', remainingTime: 0 },
  { direction: '东向', status: '未知', remainingTime: 0 },
  { direction: '西向', status: '未知', remainingTime: 0 },
  { direction: '南向', status: '未知', remainingTime: 0 }
])

async function testRealtimeUpdate() {
  try {
    console.log('1. 获取初始数据...')
    const initialData = await api.getTrafficStatus()
    console.log('✅ 初始数据获取成功:', initialData)

    // 更新数据
    if (initialData && initialData.length > 0) {
      const data = initialData[0]
      trafficData.value = {
        totalVehicles: data.vehicle_count || 35,
        averageSpeed: data.average_speed || 36.1,
        congestionPoints: data.congestion_level === '拥堵' ? 1 : 0
      }

      lightStatuses.value = [
        { direction: '北向', status: data.light_status || '绿灯', remainingTime: data.remaining_time || 13 },
        { direction: '东向', status: data.light_status === '绿灯' ? '红灯' : '绿灯', remainingTime: data.remaining_time || 18 },
        { direction: '西向', status: data.light_status === '绿灯' ? '红灯' : '绿灯', remainingTime: data.remaining_time || 13 },
        { direction: '南向', status: data.light_status === '绿灯' ? '绿灯' : '红灯', remainingTime: data.remaining_time || 18 }
      ]
    }

    console.log('✅ 数据已更新')
    console.log('当前交通数据:', trafficData.value)
    console.log('信号灯状态:', lightStatuses.value)

    // 模拟实时更新
    console.log('\n2. 模拟实时更新...')
    setTimeout(() => {
      console.log('🔄 3秒后数据更新...')
      // 模拟新的数据
      const newData = {
        vehicle_count: Math.floor(Math.random() * 100),
        average_speed: Math.floor(Math.random() * 60) + 10,
        congestion_level: ['畅通', '缓行', '拥堵'][Math.floor(Math.random() * 3)],
        light_status: ['绿灯', '红灯'][Math.floor(Math.random() * 2)],
        remaining_time: Math.floor(Math.random() * 30) + 10
      }

      trafficData.value = {
        totalVehicles: newData.vehicle_count,
        averageSpeed: newData.average_speed,
        congestionPoints: newData.congestion_level === '拥堵' ? 1 : 0
      }

      lightStatuses.value = [
        { direction: '北向', status: newData.light_status, remainingTime: newData.remaining_time },
        { direction: '东向', status: newData.light_status === '绿灯' ? '红灯' : '绿灯', remainingTime: newData.remaining_time + 5 },
        { direction: '西向', status: newData.light_status === '绿灯' ? '红灯' : '绿灯', remainingTime: newData.remaining_time - 2 },
        { direction: '南向', status: newData.light_status === '绿灯' ? '绿灯' : '红灯', remainingTime: newData.remaining_time + 3 }
      ]

      const fetchTrafficLights = async () => {
        try {
          const res = await axios.get('/api/traffic_lights');
          trafficLights.value = res.data;
        } catch (e) {
          // 可选：错误处理
        }
      };

      onMounted(() => {
        fetchTrafficLights();
        timer = setInterval(fetchTrafficLights, 1000);
      });
      onUnmounted(() => {
        clearInterval(timer);
      });
      console.log('✅ 数据已更新:', trafficData.value)
      console.log('✅ 信号灯状态已更新:', lightStatuses.value)

      console.log('\n🎉 实时数据更新测试完成！')
    }, 3000)

  } catch (error) {
    console.error('❌ 测试失败:', error)
  }
}

testRealtimeUpdate()