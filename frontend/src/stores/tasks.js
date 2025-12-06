import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from './auth'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref([])
  const loading = ref(false)

  const fetchTasks = async (skip = 0, limit = 100) => {
    loading.value = true
    try {
      const response = await api.get(`/tasks/list?skip=${skip}&limit=${limit}`)
      tasks.value = response.data.tasks || []
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
      tasks.value = []
    } finally {
      loading.value = false
    }
  }

  const createTask = async (taskData) => {
    try {
      const response = await api.post('/tasks/', taskData)
      const newTask = response.data
      tasks.value.push(newTask)
      return newTask
    } catch (error) {
      throw error
    }
  }

  const updateTask = async (taskId, taskData) => {
    try {
      const response = await api.put(`/tasks/${taskId}`, taskData)
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = response.data
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  const deleteTask = async (taskId) => {
    try {
      await api.delete(`/tasks/${taskId}`)
      tasks.value = tasks.value.filter(t => t.id !== taskId)
    } catch (error) {
      throw error
    }
  }

  const getTask = async (taskId) => {
    try {
      const response = await api.get(`/tasks/${taskId}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  const clearTasks = () => {
    tasks.value = []
  }

  const getTaskWorkers = async (taskId) => {
    try {
      const response = await api.get(`/tasks/${taskId}/workers`)
      return response.data || []
    } catch (error) {
      console.error('Failed to get task workers:', error)
      return []
    }
  }

  const addWorkerToTask = async (taskId, workerId) => {
    try {
      const response = await api.post(`/tasks/${taskId}/add-worker/${workerId}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  const removeWorkerFromTask = async (taskId, workerId) => {
    try {
      const response = await api.post(`/tasks/${taskId}/remove-worker/${workerId}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  const completeTaskByWorker = async (taskId) => {
    try {
      const authStore = useAuthStore()
      const userId = authStore.user?.id || 1
      const response = await api.post(`/tasks/${taskId}/complete?user_id=${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  return {
    tasks,
    loading,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    getTask,
    clearTasks,
    getTaskWorkers,
    addWorkerToTask,
    removeWorkerFromTask,
    completeTaskByWorker
  }
})
