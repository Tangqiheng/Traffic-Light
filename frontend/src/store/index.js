import { createStore } from 'vuex'

export default createStore({
  state: {
    trafficStatus: null,
    lightStatus: null,
    systemStatus: null,
    // 认证状态
    user: null,
    isAuthenticated: false
  },

  mutations: {
    SET_TRAFFIC_STATUS(state, status) {
      state.trafficStatus = status
    },

    SET_LIGHT_STATUS(state, status) {
      state.lightStatus = status
    },

    SET_SYSTEM_STATUS(state, status) {
      state.systemStatus = status
    },

    // 认证相关mutations
    SET_USER(state, user) {
      state.user = user
      state.isAuthenticated = !!user
    },

    LOGOUT(state) {
      state.user = null
      state.isAuthenticated = false
    }
  },

  actions: {
    updateTrafficStatus({ commit }, status) {
      commit('SET_TRAFFIC_STATUS', status)
    },

    updateLightStatus({ commit }, status) {
      commit('SET_LIGHT_STATUS', status)
    },

    updateSystemStatus({ commit }, status) {
      commit('SET_SYSTEM_STATUS', status)
    },

    // 认证相关actions
    setUser({ commit }, user) {
      commit('SET_USER', user)
    },

    logout({ commit }) {
      commit('LOGOUT')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  },

  getters: {
    trafficStatus: state => state.trafficStatus,
    lightStatus: state => state.lightStatus,
    systemStatus: state => state.systemStatus,
    user: state => state.user,
    isAuthenticated: state => state.isAuthenticated
  }
})