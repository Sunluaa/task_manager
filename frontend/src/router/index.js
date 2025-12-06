import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/new',
    name: 'NewTask',
    component: () => import('../views/NewTask.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: () => import('../views/TaskDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/users',
    name: 'Users',
    component: () => import('../views/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      if (authStore.token) {
        const isValid = await authStore.checkAuth()
        if (isValid) {
          if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
            next('/')
          } else {
            next()
          }
        } else {
          next('/login')
        }
      } else {
        next('/login')
      }
    } else {
      if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
        next('/')
      } else {
        next()
      }
    }
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
