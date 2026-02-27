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
          <!-- 用户信息与管理员功能块 -->
          <div class="user-info" v-if="isAuthenticated">
            <el-dropdown>
              <span class="el-dropdown-link">
                <el-icon><User /></el-icon>
                {{ currentUser?.username || '用户' }}
                <el-icon><SwitchButton /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="goProfile">个人信息</el-dropdown-item>
                  <el-dropdown-item @click="goChangePassword">修改密码</el-dropdown-item>
                  <el-dropdown-item v-if="currentUser && currentUser.is_admin" @click="router.push('/admin')">管理员功能</el-dropdown-item>
                  <el-dropdown-item v-if="currentUser && currentUser.is_admin" @click="router.push('/admin/logs')">操作日志</el-dropdown-item>
                  <el-dropdown-item v-if="currentUser && currentUser.is_admin" @click="router.push('/admin/permissions')">权限分配</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <keep-alive :include="cachedViews">
          <router-view :key="route.fullPath" />
        </keep-alive>
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
// 需要缓存的页面名
const cachedViews = ref(['Dashboard'])

// 根据当前路由设置激活的菜单项
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
  if (path) router.push(path)
  activeIndex.value = key
}

const currentUser = computed(() => store.getters.user)
const isAuthenticated = computed(() => store.getters.isAuthenticated)

const fetchUserInfo = async () => {
  try {
    const response = await getCurrentUser()
    store.dispatch && store.dispatch('setUser', response.data)
  } catch (error) {
    console.error('获取用户信息失败:', error)
    // 只清空user，不强制登出，避免频繁跳登录
    store.dispatch && store.dispatch('setUser', null)
  }
}

const handleLogout = () => {
  store.dispatch && store.dispatch('logout')
  authLogout()
  ElMessage.success('已退出登录')
  // 不用router.push，authLogout已跳转
}

const goHome = () => { router.push('/') }
const goProfile = () => { router.push('/profile') }
const goChangePassword = () => { router.push('/change-password') }

// 监听路由变化，更新菜单激活状态
watch(route, () => {
  setActiveMenu()
}, { immediate: true })

onMounted(async () => {
  const token = localStorage.getItem('access_token')
  // 没有token直接跳转登录页（防止直接访问主界面）
  if (!token) {
    router.replace('/login')
    return
  }
  // 无论是否有user，都尝试拉取一次，保证刷新后也能获取到
  await fetchUserInfo()
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
.navigation-menu :deep(.el-menu-item:hover) { background-color: rgba(255, 255, 255, 0.1) !important; }
.navigation-menu :deep(.el-menu-item.is-active) { background-color: transparent !important; border-bottom: 3px solid #fff !important; color: #fff !important; font-weight: 600; }
.navigation-menu :deep(.el-sub-menu__title) { color: #fff !important; height: 70px !important; line-height: 70px !important; }

/* 修改数据分析模块悬停样式 - 避免纯白色背景，采用浅色蒙层效果 */
:deep(.el-sub-menu__title:hover) {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05)) !important;
  color: #fff !important;
}

.user-info { flex-shrink: 0 }
.el-dropdown-link { cursor: pointer; color: #fff; display: flex; align-items: center }
.main-content { background-color: #f8fafc; color: #333; padding: 20px; min-height: calc(100vh - 122px) }
.footer { text-align: center; padding: 15px; color: #606266; font-size: 14px; background-color: #fff; border-top: 1px solid #ebeef5 }
</style>