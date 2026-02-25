import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../services/auth.js'
import Login from '../views/Login.vue'
import Profile from '../views/Profile.vue'
import ChangePassword from '../views/ChangePassword.vue'
import Monitor from '../views/Monitor.vue'

const routes = [
    { path: '/', name: 'Home', component: Monitor, meta: { requiresAuth: true } },
    { path: '/login', name: 'Login', component: Login, meta: { requiresAuth: false } },
    { path: '/monitor', name: 'Monitor', component: Monitor, meta: { requiresAuth: true } },
    { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
    { path: '/change-password', name: 'ChangePassword', component: ChangePassword, meta: { requiresAuth: true } }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const requiresAuth = to.meta.requiresAuth === true
    if (requiresAuth && !isAuthenticated()) {
        next('/login')
    } else {
        next()
    }
})

export default router
