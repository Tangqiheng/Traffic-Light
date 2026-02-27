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
  }
}

// 默认导出API服务对象
export default apiService