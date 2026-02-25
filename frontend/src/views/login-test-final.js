// 测试登录功能
import axios from 'axios'

console.log('=== 登录功能测试 ===')

// 清除本地存储
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')

console.log('1. 测试登录API...')
axios.post('http://localhost:8001/api/auth/login', {
  username: 'admin',
  password: 'admin123'
}, {
  headers: {
    'Content-Type': 'application/json'
  }
}).then(response => {
  console.log('✅ 登录API调用成功')
  console.log('返回数据:', response.data)
  
  // 检查数据格式
  if (response.data.access_token && response.data.token_type) {
    console.log('✅ 返回格式正确')
    
    // 存储token
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token || '')
    
    console.log('✅ token已存储')
    
    // 测试获取用户信息
    console.log('2. 测试获取用户信息...')
    axios.get('http://localhost:8001/api/user/profile', {
      headers: {
        'Authorization': `Bearer ${response.data.access_token}`
      }
    }).then(profileRes => {
      console.log('✅ 用户信息获取成功')
      console.log('用户信息:', profileRes.data)
      
      console.log('=== 测试完成 ===')
      console.log('🎉 登录功能正常工作！')
    }).catch(err => {
      console.error('❌ 获取用户信息失败:', err)
    })
  } else {
    console.error('❌ 返回格式不符合预期')
  }
}).catch(error => {
  console.error('❌ 登录API调用失败:', error)
})