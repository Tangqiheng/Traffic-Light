import { createRouter, createWebHistory } from 'vue-router'
import Monitor from '../views/Monitor.vue'
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: Monitor,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('../views/ChangePassword.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue'),
    meta: { requiresAuth: true }
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
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')

  // 如果需要认证但没有token，跳转到登录页
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login' })
  }
  // 如果不需要认证但有token，且是登录页，跳转到首页
  else if (!to.meta.requiresAuth && token && to.name === 'Login') {
    next({ name: 'Home' })
  }
  // 其他情况正常导航
  else {
    next()
  }
})

export default router