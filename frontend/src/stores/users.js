import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useUsersStore = defineStore('users', () => {
  const users = ref([])
  const loading = ref(false)

  const fetchUsers = async (skip = 0, limit = 100) => {
    loading.value = true
    try {
      const response = await api.get(`/auth/users?skip=${skip}&limit=${limit}`)
      users.value = response.data || []
    } catch (error) {
      console.error('Failed to fetch users:', error)
      users.value = []
    } finally {
      loading.value = false
    }
  }

  const createUser = async (userData) => {
    try {
      const response = await api.post('/auth/users', userData)
      users.value.push(response.data)
      return response.data
    } catch (error) {
      throw error
    }
  }

  const updateUser = async (userId, userData) => {
    try {
      const response = await api.put(`/auth/users/${userId}`, userData)
      const index = users.value.findIndex(u => u.id === userId)
      if (index !== -1) {
        users.value[index] = response.data
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  const deleteUser = async (userId) => {
    try {
      await api.delete(`/auth/users/${userId}`)
      users.value = users.value.filter(u => u.id !== userId)
    } catch (error) {
      throw error
    }
  }

  const clearUsers = () => {
    users.value = []
  }

  return {
    users,
    loading,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    clearUsers
  }
})
