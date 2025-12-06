import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from './auth'

export const useCommentsStore = defineStore('comments', () => {
  const comments = ref([])
  const history = ref([])
  const loading = ref(false)

  const fetchComments = async (taskId) => {
    loading.value = true
    try {
      const response = await api.get(`/tasks/${taskId}/comments`)
      comments.value = response.data || []
    } catch (error) {
      console.error('Failed to fetch comments:', error)
      comments.value = []
    } finally {
      loading.value = false
    }
  }

  const fetchHistory = async (taskId) => {
    loading.value = true
    try {
      const response = await api.get(`/tasks/${taskId}/history`)
      history.value = response.data || []
    } catch (error) {
      console.error('Failed to fetch history:', error)
      history.value = []
    } finally {
      loading.value = false
    }
  }

  const addComment = async (taskId, text) => {
    try {
      const authStore = useAuthStore()
      const fullName = authStore.user?.full_name || authStore.user?.email || 'Unknown User'
      
      const response = await api.post(`/tasks/${taskId}/comments`, { 
        text,
        full_name: fullName
      })
      comments.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to add comment:', error)
      throw error
    }
  }

  const clearComments = () => {
    comments.value = []
    history.value = []
  }

  return {
    comments,
    history,
    loading,
    fetchComments,
    fetchHistory,
    addComment,
    clearComments
  }
})
