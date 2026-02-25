<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header-container">
        <div class="header-content">
          <div class="logo-container" @click="goHome">
            <div class="logo-svg">
              <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                <rect x="5" y="5" width="30" height="30" rx="5" fill="#409EFF"/>
                <circle cx="20" cy="15" r="3" fill="#FFD700"/>
                <circle cx="20" cy="22" r="3" fill="#FFA500"/>
                <circle cx="20" cy="29" r="3" fill="#FF4500"/>
                <rect x="15" y="8" width="10" height="24" rx="2" fill="#E6E6FA" opacity="0.3"/>
              </svg>
            </div>
            <h1 class="logo-text">智能交通灯控制系统</h1>
          </div>
          <el-menu
            :default-active="activeIndex"
            class="navigation-menu"
            mode="horizontal"
            :ellipsis="false"
            @select="handleSelect"
          >
            <el-menu-item index="1" route="/">
              <el-icon><House /></el-icon>系统概览
            </el-menu-item>
            <el-menu-item index="2" route="/monitor">
              <el-icon><Monitor /></el-icon>实时监控
            </el-menu-item>
            <el-menu-item index="3" route="/control">
              <el-icon><Operation /></el-icon>信号控制
            </el-menu-item>
            <el-sub-menu index="4">
              <template #title>
                <el-icon><DataAnalysis /></el-icon>
                数据分析
              </template>
              <el-menu-item index="4-1" route="/history">历史数据</el-menu-item>
              <el-menu-item index="4-2" route="/reports">统计报告</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="5" route="/settings">
              <el-icon><Setting /></el-icon>系统设置
            </el-menu-item>
          </el-menu>
          <div class="user-info" v-if="isAuthenticated">
            <el-dropdown>
              <span class="el-dropdown-link">
                <el-icon><User /></el-icon>
                {{ currentUser?.username || '用户' }}
                <el-icon class="el-icon--right"><SwitchButton /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="goProfile">个人中心</el-dropdown-item>
                  <el-dropdown-item @click="goChangePassword">修改密码</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
      
      <el-footer class="footer">
        智能交通灯控制系统 ©2023 | 多模态智能交通管理系统
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import {
  House,
  Operation,
  DataAnalysis,
  Setting,
  Monitor,
  User,
  SwitchButton
} from '@element-plus/icons-vue'
import { getCurrentUser, logout as authLogout } from './services/auth.js'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const store = useStore()

const activeIndex = ref('1')

const setActiveMenu = () => {
  const pathMap = {
    '/': '1',
    '/monitor': '2',
    '/control': '3',
    '/history': '4-1',
    '/reports': '4-2',
    '/settings': '5'
  }
  activeIndex.value = pathMap[route.path] || '1'
}

const handleSelect = (key) => {
  const map = {
    '1': '/',
    '2': '/monitor',
    '3': '/control',
    '4-1': '/history',
    '4-2': '/reports',
    '5': '/settings'
  }
  const path = map[key]
  if (path) {
    if (route.path === path) {
      // 如果是当前页面，强制刷新
      router.replace({ path: '/redirect' }).then(() => {
        router.replace({ path })
      })
    } else {
      router.push(path)
    }
  }
  activeIndex.value = key
}

const currentUser = computed(() => store.getters?.user)
const isAuthenticated = computed(() => !!localStorage.getItem('access_token'))

const fetchUserInfo = async () => {
  try {
    const response = await getCurrentUser()
    store.dispatch && store.dispatch('setUser', response.data)
  } catch (error) {
    console.error('获取用户信息失败:', error)
    handleLogout()
  }
}

const handleLogout = () => {
  store.dispatch && store.dispatch('logout')
  authLogout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const goHome = () => { router.push('/') }
const goProfile = () => { router.push('/profile') }
const goChangePassword = () => { router.push('/change-password') }

watch(route, () => {
  setActiveMenu()
}, { immediate: true })

onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (token) fetchUserInfo()
})
</script>

<style scoped>
/* styles kept as before */
.header-container {
  background: linear-gradient(90deg, #409EFF, #3a7aff, #2e67c3);
  color: #fff;
  padding: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  height: 70px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo-container { display: flex; align-items: center; flex-shrink: 0; cursor: pointer }
.logo-svg { margin-right: 15px }
.logo-text { color: #fff; font-size: 18px; font-weight: 600; margin-left: 10px; letter-spacing: 0.5px }
.navigation-menu { border: none !important; background: transparent; flex: 1; margin: 0 30px; max-width: 700px }
.navigation-menu :deep(.el-menu-item) { color: #fff !important; height: 70px !important; line-height: 70px !important; border-bottom: 3px solid transparent !important }
.navigation-menu :deep(.el-menu-item:hover) { background-color: rgba(255, 255, 255, 0.1) !important }
.navigation-menu :deep(.el-menu-item.is-active) { background-color: transparent !important; border-bottom: 3px solid #fff !important; color: #fff !important; font-weight: 600 }
.navigation-menu :deep(.el-sub-menu__title) { color: #fff !important; height: 70px !important; line-height: 70px !important }
.user-info { flex-shrink: 0 }
.el-dropdown-link { cursor: pointer; color: #fff; display: flex; align-items: center }
.main-content { background-color: #f8fafc; color: #333; padding: 20px; min-height: calc(100vh - 122px) }
.footer { text-align: center; padding: 15px; color: #606266; font-size: 14px; background-color: #fff; border-top: 1px solid #ebeef5 }
</style>