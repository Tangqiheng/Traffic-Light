import authClient from './auth.js'

export const updateProfile = (data) => authClient.put('/auth/me', data)
export const changePassword = (data) => authClient.post('/auth/change_password', data)

export default {
    getTrafficStatus(intersectionId) {
        return authClient.get(`/v1/traffic/status/${intersectionId}`)
    },
    getTrafficLightStatus(intersectionId) {
        return authClient.get(`/v1/traffic/light/${intersectionId}`)
    },
    getTrafficHistory(limit = 50) {
        return authClient.get(`/traffic/history?limit=${limit}`)
    },
    getTrafficStatistics(hours = 24) {
        return authClient.get(`/traffic/statistics?hours=${hours}`)
    },
    sendControlCommand(command) {
        return authClient.post('/v1/control', command)
    },
    getSystemStatus() {
        return authClient.get('/system/status')
    },
    getSystemConfig() {
        return authClient.get('/system/config')
    },
    getControlLogs(limit = 10) {
        return authClient.get(`/control/logs?limit=${limit}`)
    },
    updateProfile(payload) {
        return updateProfile(payload)
    },
    changePassword(payload) {
        return changePassword(payload)
    }
}
