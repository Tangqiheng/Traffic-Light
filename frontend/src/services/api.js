// 管理员获取指定用户信息
export const getUserById = (userId) => authClient.get(`/admin/users/${userId}`)
// 管理员更新指定用户信息
export const updateUserById = (userId, data) => authClient.put(`/admin/users/${userId}`, data)
// 管理员重置指定用户密码
export const adminResetPassword = (userId, newPassword) => authClient.post(`/admin/users/${userId}/reset_password`, { new_password: newPassword })
// 注册新用户
export const register = (data) => {
  return import('axios').then(({ default: axios }) =>
    axios.post('/api/auth/register', data)
  )
}

// 管理员获取用户列表
export const getAllUsers = () => {
  return import('./auth.js').then(({ default: authClient }) =>
    authClient.get('/admin/users')
  )
}
import authClient from './auth.js'

// 简单用户相关API的命名导出，供页面直接调用
export const updateProfile = (data) => authClient.put('/user/profile', data)
export const changePassword = (data) => authClient.post('/auth/change_password', data)

// API服务对象
const apiService = {
  // 交通状态相关API
  // 获取实时交通状态，支持 intersectionId
  getTrafficStatus(intersectionId) {
    // intersectionId 可选，默认 intersection_001
    const id = intersectionId || 'intersection_001';
    return authClient.get(`/traffic/data?intersection_id=${id}`).then(response => response.data)
  },

  // 获取信号灯状态
  getTrafficLightStatus(intersectionId) {
    const id = intersectionId || 'intersection_001';
    return authClient.get(`/traffic/light_status?intersection_id=${id}`).then(response => response.data)
  },

  // 历史数据相关API
  getTrafficHistory(limit = 50, intersectionId) {
    const id = intersectionId || 'intersection_001';
    return authClient.get(`/traffic/history?intersection_id=${id}&limit=${limit}`).then(response => response.data)
  },

  // 统计数据接口
  getTrafficStatistics(hours = 24, intersectionId) {
    const id = intersectionId || 'intersection_001';
    return authClient.get(`/traffic/statistics?intersection_id=${id}&hours=${hours}`).then(response => response.data)
  },

  // 控制相关API
  sendControlCommand(command) {
    return authClient.post('/traffic/update', command).then(response => response.data)
  },

  // 系统相关API
  getSystemStatus() {
    return authClient.get('/system/status').then(response => response.data)
  },

  getSystemConfig() {
    return authClient.get('/system/config').then(response => response.data)
  },

  getControlLogs(limit = 10) {
    return authClient.get(`/control/logs?limit=${limit}`).then(response => response.data)
  },

  // 用户相关（也通过命名导出可直接使用）
  updateProfile(payload) {
    return updateProfile(payload)
  },

  changePassword(payload) {
    return changePassword(payload)
  },

  // 批量更新用户排序
  sortUsers(payload) {
    return authClient.post('/admin/users/sort', { sort_list: payload });
  }
}

// 默认导出API服务对象
export default apiService

// 管理员批量更新用户排序
export const sortUsers = (sortList) => authClient.post('/admin/users/sort', { sort_list: sortList })