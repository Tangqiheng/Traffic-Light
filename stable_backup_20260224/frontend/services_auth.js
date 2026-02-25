import axios from 'axios'

const authClient = axios.create({
    baseURL: '/api',
    timeout: 10000
})

authClient.interceptors.request.use(
    config => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => Promise.reject(error)
)

authClient.interceptors.response.use(
    response => response,
    async error => {
        if (error.response?.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
                try {
                    const refreshResponse = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
                    const newAccessToken = refreshResponse.data.access_token
                    localStorage.setItem('access_token', newAccessToken)
                    error.config.headers.Authorization = `Bearer ${newAccessToken}`
                    return authClient.request(error.config)
                } catch (refreshError) {
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')
                    window.location.href = '/login'
                    return Promise.reject(refreshError)
                }
            } else {
                localStorage.removeItem('access_token')
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default authClient

export const login = (username, password) => axios.post('/api/auth/login', { username, password })
export const getCurrentUser = () => authClient.get('/auth/me')
export const logout = () => { localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); window.location.href = '/login' }
