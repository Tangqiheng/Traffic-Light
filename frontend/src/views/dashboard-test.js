// 测试Dashboard组件导入
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/services/api.js'

console.log('Dashboard组件导入测试:')
console.log('api对象:', typeof api)
console.log('api.getTrafficStatus:', typeof api.getTrafficStatus)
console.log('导入测试成功!')