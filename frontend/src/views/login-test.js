// 测试登录页面访问
import axios from 'axios'

// 清除本地存储的token（如果存在）
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')

console.log('清除token后，尝试访问登录页面...')
console.log('当前URL:', window.location.href)

// 检查是否重定向到登录页
if (window.location.pathname === '/login') {
  console.log('✅ 成功跳转到登录页面')
} else {
  console.log('❌ 未正确跳转到登录页面')
}

// 尝试直接访问登录页面
setTimeout(() => {
  console.log('尝试手动导航到登录页面...')
  window.location.href = '/login'
}, 1000)