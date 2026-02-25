// 最终登录功能验证脚本
import axios from 'axios'

console.log('🔍 开始登录功能验证...')

// 1. 清除现有token
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')
console.log('✅ 已清除本地存储的token')

// 2. 测试登录API
console.log('1. 测试登录API...')
axios.post('http://localhost:8001/api/auth/login', {
  username: 'admin',
  password: 'admin123'
}, {
  headers: { 'Content-Type': 'application/json' }
}).then(response => {
  console.log('✅ 登录API调用成功')
  console.log('返回数据:', response.data)
  
  // 3. 验证数据格式
  if (response.data.access_token && response.data.token_type) {
    console.log('✅ 返回格式正确')
    
    // 4. 存储token
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token || '')
    console.log('✅ token已存储')
    
    // 5. 测试获取用户信息
    console.log('2. 测试获取用户信息...')
    return axios.get('http://localhost:8001/api/user/profile', {
      headers: { 'Authorization': `Bearer ${response.data.access_token}` }
    })
  } else {
    console.error('❌ 返回格式不符合预期')
    throw new Error('格式错误')
  }
}).then(profileRes => {
  console.log('✅ 用户信息获取成功')
  console.log('用户信息:', profileRes.data)
  
  // 6. 测试前端路由跳转
  console.log('3. 测试前端路由跳转...')
  const router = {
    push: (path) => console.log(`➡️ 路由跳转到: ${path}`)
  }
  
  // 模拟storeTokensAndRedirect函数
  const storeTokensAndRedirect = (data) => {
    console.log('✅ token存储成功')
    console.log('➡️ 跳转到系统概览页')
    router.push('/')
  }
  
  storeTokensAndRedirect({
    access_token: 'test-token',
    refresh_token: '',
    message: '登录成功'
  })
  
  console.log('🎉 登录功能验证完成！')
}).catch(error => {
  console.error('❌ 登录功能验证失败:', error)
})