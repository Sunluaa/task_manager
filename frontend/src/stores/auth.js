import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token') || null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (email, password) => {
    loading.value = true
    try {
      const response = await api.post('/auth/login', { email, password })
      const data = response.data
      
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('auth_token', data.access_token)
      
      return data
    } catch (error) {
      // Clear authentication state on error
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
      throw error
    } finally {
      loading.value = false
    }
  }

  const checkAuth = async () => {
    if (!token.value) return false
    
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      return true
    } catch (error) {
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
      return false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    checkAuth,
    logout
  }
})
