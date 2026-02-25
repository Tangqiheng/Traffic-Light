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
authClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // 认证失败，清除token并跳转登录
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default authClient

// 认证相关API
export const login = (username, password) => {
  return axios.post('/api/auth/login', {
    username,
    password
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