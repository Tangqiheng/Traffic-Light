import axios from 'axios'

const authClient = axios.create({
  baseURL: '/api',  // 使用相对路径，通过Vite代理转发到后端
  timeout: 10000
})

// 请求拦截器：添加token
authClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理认证错误
// 防止401弹窗/跳转频繁触发
let isHandling401 = false
authClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401 && !isHandling401) {
      isHandling401 = true
      localStorage.removeItem('access_token')
      // 延迟跳转，避免多次401时多次跳转
      setTimeout(() => {
        isHandling401 = false
        window.location.href = '/login'
      }, 500)
    }
    return Promise.reject(error)
  }
)

export default authClient

// 认证相关API
// 只允许传递已截断的 safePassword，防止误用原始 password
export const login = (username, safePassword) => {
  return axios.post('/api/auth/login', {
    username,
    password: safePassword
  }).then(response => response.data) // 返回data而不是整个response对象
}

export const getCurrentUser = () => {
  return authClient.get('/user/profile')
}

export const logout = () => {
  localStorage.removeItem('access_token')
  window.location.href = '/login'
}

// 检查是否已登录
export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token')
}