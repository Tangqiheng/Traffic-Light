// ...existing code...
import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'
import { getCurrentUser } from '../services/auth'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('../views/Monitor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/control',
    name: 'Control',
    component: () => import('../views/Control.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile/:userId?',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/change-password/:userId?',
    name: 'ChangePassword',
    component: () => import('../views/ChangePassword.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/logs',
    name: 'OperationLog',
    component: () => import('../views/OperationLog.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/permissions',
    name: 'PermissionAssign',
    component: () => import('../views/PermissionAssign.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/redirect',
    name: 'Redirect',
    component: { template: '<div></div>' },
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：检查认证状态
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('access_token')
  // 需要认证的页面
  if (to.meta.requiresAuth) {
    if (!token) {
      // 只要没有token，访问任何需要认证的页面都跳转登录
      if (to.name !== 'Login') {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    } else {
      // token存在但user未拉取，尝试拉取
      if (!store.getters.isAuthenticated) {
        try {
          const res = await getCurrentUser()
          store.dispatch('setUser', res.data)
          next()
        } catch (e) {
          // token失效，清除并跳转登录
          store.dispatch('logout')
          localStorage.removeItem('access_token')
          next({ name: 'Login' })
        }
        return
      }
      next()
    }
  } else if (!to.meta.requiresAuth && token && to.name === 'Login') {
    // 已登录访问登录页，跳转首页
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router