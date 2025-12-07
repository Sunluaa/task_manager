<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 to-orange-100">
    <nav class="bg-white shadow">
      <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <router-link to="/" class="text-2xl font-bold text-orange-600">Задачи</router-link>
        <button @click="handleLogout" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition">
          Выход
        </button>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto px-4 py-8">
      <router-link to="/" class="text-orange-600 hover:text-orange-700 mb-4 inline-block font-semibold">
        ← К задачам
      </router-link>

      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>

      <div v-else-if="task" class="grid gap-8">
        <!-- Task Details -->
        <div class="bg-white rounded-lg shadow-md p-8">
          <div class="mb-6">
            <h1 class="text-3xl font-bold text-gray-900">{{ task.title }}</h1>
            <p class="text-gray-600 mt-2">{{ task.description }}</p>
          </div>

          <!-- Admin only: Status and Priority controls -->
          <div v-if="authStore.user?.role === 'admin'" class="grid grid-cols-2 gap-4 mb-8">
            <div>
              <span class="text-sm text-gray-600 font-semibold">Статус</span>
              <select
                v-model="form.status"
                class="w-full mt-2 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none"
              >
                <option value="new">Новая</option>
                <option value="in_progress">В процессе</option>
                <option value="completed">Завершена</option>
              </select>
            </div>

            <div>
              <span class="text-sm text-gray-600 font-semibold">Приоритет</span>
              <select
                v-model="form.priority"
                class="w-full mt-2 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none"
              >
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
                <option value="urgent">Срочный</option>
              </select>
            </div>
          </div>

          <!-- Worker: Show status and priority as read-only badges -->
          <div v-else class="mb-8 flex gap-4">
            <span :class="getStatusBadgeClass(task.status)">
              {{ formatStatus(task.status) }}
            </span>
            <span :class="getPriorityBadgeClass(task.priority)">
              {{ formatPriority(task.priority) }}
            </span>
          </div>

          <!-- Admin only: Description editor -->
          <div v-if="authStore.user?.role === 'admin'" class="mb-8">
            <label class="block text-sm font-medium text-gray-700 mb-2">Описание</label>
            <textarea
              v-model="form.description"
              rows="4"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none"
            ></textarea>
          </div>

          <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-800 text-sm">{{ error }}</p>
          </div>

          <!-- Admin only: Save and Delete buttons -->
          <div v-if="authStore.user?.role === 'admin'" class="flex gap-4">
            <button
              @click="handleUpdate"
              :disabled="saving"
              class="flex-1 bg-orange-600 hover:bg-orange-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button
              @click="handleDelete"
              :disabled="saving"
              class="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Удалить
            </button>
          </div>
        </div>

        <!-- Assigned Workers Section (Admin can manage, Workers can see) -->
        <div class="bg-white rounded-lg shadow-md p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Назначенные исполнители</h2>
          <!-- Admin section: Add worker -->
          <div v-if="authStore.user?.role === 'admin'" class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Добавить исполнителя</label>
            <div v-if="!canEditWorkers" class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg mb-3">
              <p class="text-yellow-800 text-sm">Можно добавлять/удалять исполнителей только для новых задач</p>
            </div>
            <div class="flex gap-2">
              <select
                v-model="selectedUserId"
                :disabled="!canEditWorkers"
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">Выберите исполнителя...</option>
                <option v-for="user in availableWorkers" :key="user.id" :value="user.id">
                  {{ user.full_name || user.email }}
                </option>
              </select>
              <button
                @click="addWorker"
                :disabled="!selectedUserId || assigning || !canEditWorkers"
                class="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ assigning ? 'Добавление...' : 'Добавить' }}
              </button>
            </div>
          </div>

          <!-- List of assigned workers -->
          <div v-if="loadingWorkers" class="text-center py-4">
            <p class="text-gray-500">Загрузка исполнителей...</p>
          </div>
          <div v-else-if="assignedWorkers.length === 0" class="py-4">
            <p class="text-gray-500">Исполнители не назначены</p>
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="worker in assignedWorkers"
              :key="worker.id"
              class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
            >
              <span class="font-medium text-gray-900">{{ worker.full_name || worker.email }}</span>
              <div class="flex gap-2">
                <span v-if="isWorkerCompleted(worker.id)" class="text-green-600 font-semibold">Выполнено</span>
                <button
                  v-if="authStore.user?.role === 'admin'"
                  @click="removeWorker(worker.id)"
                  :disabled="assigning || !canEditWorkers"
                  class="text-red-600 hover:text-red-800 font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Worker Complete Button -->
        <div v-if="authStore.user?.role === 'user' && isAssignedToTask" class="bg-white rounded-lg shadow-md p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Завершение задачи</h2>
          <div v-if="hasCompletedTask" class="p-4 bg-green-50 border border-green-200 rounded-lg mb-4">
            <p class="text-green-800 font-semibold">Вы отметили эту задачу как выполненную</p>
          </div>
          <button
            v-else
            @click="completeTask"
            :disabled="completing"
            class="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ completing ? 'Отметка как выполненной...' : 'Отметить как выполненную' }}
          </button>
        </div>

        <!-- Admin: Worker Completion Status -->
        <div v-if="authStore.user?.role === 'admin'" class="bg-white rounded-lg shadow-md p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Статус исполнителей</h2>
          <div class="space-y-4 mb-6">
            <div
              v-for="worker in assignedWorkers"
              :key="worker.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
            >
              <div>
                <p class="font-semibold text-gray-900">{{ worker.full_name || worker.email }}</p>
            <div v-if="isWorkerCompleted(worker.id)" class="text-sm text-green-600 font-medium">Выполнено</div>
                <p v-else class="text-sm text-yellow-600 font-medium">Ожидание</p>
              </div>
            </div>
          </div>

          <!-- Admin Action Buttons -->
          <div v-if="allWorkersCompleted && task?.status !== 'completed'" class="flex gap-4">
            <button
              @click="approveTask"
              :disabled="approving"
              class="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ approving ? 'Подтверждение...' : 'Завершить' }}
            </button>
            <button
              @click="reworkTask"
              :disabled="reworking"
              class="flex-1 px-6 py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ reworking ? 'Отправка...' : 'Вернуть на доработку' }}
            </button>
          </div>
          <div v-else-if="task?.status === 'completed'" class="p-4 bg-green-50 border border-green-200 rounded-lg text-center">
            <p class="text-green-800 font-medium">Задача завершена</p>
          </div>
          <div v-else class="p-4 bg-orange-50 border border-orange-200 rounded-lg text-center">
            <p class="text-orange-800 font-medium">Ожидание выполнения всеми исполнителями</p>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="bg-white rounded-lg shadow-md p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Комментарии</h2>

          <!-- Add Comment Form -->
          <div class="mb-6 p-4 bg-gray-50 rounded-lg">
            <textarea
              v-model="newComment"
              placeholder="Добавить комментарий..."
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none mb-3"
            ></textarea>
            <button
              @click="addComment"
              :disabled="!newComment.trim() || commenting"
              class="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ commenting ? 'Отправка...' : 'Отправить' }}
            </button>
          </div>

          <!-- Comments List -->
          <div v-if="commentsStore.loading" class="text-center py-4">
            <p class="text-gray-500">Загрузка комментариев...</p>
          </div>
          <div v-else-if="commentsStore.comments.length === 0" class="py-4">
            <p class="text-gray-500">Комментариев нет</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="comment in commentsStore.comments"
              :key="comment.id"
              class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              <div class="flex justify-between items-start mb-2">
                <p class="font-semibold text-gray-900">{{ comment.full_name || `Пользователь #${comment.user_id}` }}</p>
                <p class="text-xs text-gray-500">{{ formatDate(comment.created_at) }}</p>
              </div>
              <p class="text-gray-700">{{ comment.text }}</p>
            </div>
          </div>
        </div>

        <!-- History Section -->
        <div class="bg-white rounded-lg shadow-md p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">История</h2>
          <div v-if="commentsStore.loading" class="text-center py-4">
            <p class="text-gray-500">Загрузка истории...</p>
          </div>
          <div v-else-if="commentsStore.history.length === 0" class="py-4">
            <p class="text-gray-500">История отсутствует</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="item in commentsStore.history"
              :key="item.id"
              class="flex gap-4 pb-4 border-b last:border-b-0"
            >
              <div class="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 font-semibold flex-shrink-0">
                {{ getHistoryIcon(item.event_type) }}
              </div>
              <div class="flex-1">
                <p class="font-semibold text-gray-900">{{ formatHistoryEvent(item.event_type) }}</p>
                <p class="text-sm text-gray-600 mt-1">{{ item.details }}</p>
                <p class="text-xs text-gray-500 mt-2">{{ formatDate(item.created_at) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-12">
        <p class="text-gray-600">Задача не найдена</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTasksStore } from '../stores/tasks'
import { useAuthStore } from '../stores/auth'
import { useCommentsStore } from '../stores/comments'
import { useUsersStore } from '../stores/users'
import api from '../services/api'

const router = useRouter()
const route = useRoute()
const tasksStore = useTasksStore()
const authStore = useAuthStore()
const commentsStore = useCommentsStore()
const usersStore = useUsersStore()

const task = ref(null)
const form = ref({
  title: '',
  description: '',
  status: 'new',
  priority: 'medium'
})

const newComment = ref('')
const loading = ref(true)
const saving = ref(false)
const commenting = ref(false)
const error = ref(null)

// Worker management
const selectedUserId = ref('')
const assignedWorkers = ref([]) // Changed: now will store full worker objects {id, full_name, email, ...}
const assignedWorkerIds = ref([]) // Keep track of just IDs for compatibility
const availableWorkers = ref([])
const loadingWorkers = ref(false)
const assigning = ref(false)

// Helper to check if task status allows editing workers
const canEditWorkers = computed(() => {
  return task.value?.status === 'new'
})

// Worker completion
const completing = ref(false)
const hasCompletedTask = ref(false)
const approving = ref(false)
const reworking = ref(false)

const isAssignedToTask = computed(() => {
  return assignedWorkerIds.value.includes(authStore.user?.id)
})

const allWorkersCompleted = computed(() => {
  if (!assignedWorkerIds.value || assignedWorkerIds.value.length === 0) {
    return false
  }
  return assignedWorkerIds.value.every(workerId => isWorkerCompleted(workerId))
})

const loadTask = async () => {
  try {
    const data = await tasksStore.getTask(route.params.id)
    task.value = data
    form.value = {
      title: data.title,
      description: data.description,
      status: data.status,
      priority: data.priority
    }
    
    // Load comments and history
    await commentsStore.fetchComments(route.params.id)
    await commentsStore.fetchHistory(route.params.id)
    
    // Load workers assigned to this task
    await loadAssignedWorkers()
    
    // Load available workers if admin
    if (authStore.user?.role === 'admin') {
      await loadAvailableWorkers()
    }
  } catch (err) {
    error.value = 'Ошибка при загрузке задачи'
  } finally {
    loading.value = false
  }
}

const loadAssignedWorkers = async () => {
  loadingWorkers.value = true
  try {
    // Get worker IDs
    const response = await api.get(`/tasks/${route.params.id}/workers`)
    assignedWorkerIds.value = response.data || []
    
    // Get all users to fetch full info for assigned workers
    const allUsersResponse = await api.get('/auth/users')
    const allUsers = allUsersResponse.data || []
    
    // Build assigned workers array with full info
    assignedWorkers.value = assignedWorkerIds.value
      .map(workerId => allUsers.find(u => u.id === workerId))
      .filter(w => w !== undefined)
    
    // Check if current user has completed this task
    if (task.value?.worker_completions) {
      hasCompletedTask.value = task.value.worker_completions.some(
        wc => wc.worker_id === authStore.user?.id
      )
    }
  } catch (err) {
    console.error('Failed to load workers:', err)
    assignedWorkers.value = []
    assignedWorkerIds.value = []
  } finally {
    loadingWorkers.value = false
  }
}

const loadAvailableWorkers = async () => {
  try {
    // Load all users and filter for active non-admin users only
    const response = await api.get('/auth/users')
    const allUsers = response.data || []
    console.log('All users from API:', allUsers)
    
    const filtered = allUsers.filter(user => 
      user.role !== 'admin' && 
      user.is_active && 
      !assignedWorkerIds.value.includes(user.id)
    )
    console.log('Filtered active workers:', filtered)
    
    availableWorkers.value = filtered
  } catch (err) {
    console.error('Failed to load available workers:', err)
    availableWorkers.value = []
  }
}

const addWorker = async () => {
  if (!selectedUserId.value) return
  if (!canEditWorkers.value) {
    alert('Можно добавлять исполнителей только для новых задач')
    return
  }
  
  assigning.value = true
  try {
    const response = await api.post(
      `/tasks/${route.params.id}/add-worker/${selectedUserId.value}`
    )
    
    assignedWorkerIds.value.push(parseInt(selectedUserId.value))
    selectedUserId.value = ''
    await loadAvailableWorkers()
    await loadAssignedWorkers()
    
    // Reload comments and history to show updated data
    await commentsStore.fetchHistory(route.params.id)
  } catch (err) {
    alert('Ошибка при добавлении исполнителя')
  } finally {
    assigning.value = false
  }
}

const removeWorker = async (workerId) => {
  if (!canEditWorkers.value) {
    alert('Можно удалять исполнителей только для новых задач')
    return
  }
  
  if (!confirm('Удалить исполнителя из задачи?')) return
  
  assigning.value = true
  try {
    const response = await api.post(
      `/tasks/${route.params.id}/remove-worker/${workerId}`
    )
    
    assignedWorkerIds.value = assignedWorkerIds.value.filter(id => id !== workerId)
    assignedWorkers.value = assignedWorkers.value.filter(w => w.id !== workerId)
    await loadAvailableWorkers()
    
    // Reload comments and history to show updated data
    await commentsStore.fetchHistory(route.params.id)
  } catch (err) {
    alert('Ошибка при удалении исполнителя')
  } finally {
    assigning.value = false
  }
}

const completeTask = async () => {
  if (!confirm('Отметить задачу как выполненную?')) return
  
  completing.value = true
  try {
    const userId = authStore.user?.id || 1
    const response = await api.post(`/tasks/${route.params.id}/complete?user_id=${userId}`)
    
    hasCompletedTask.value = true
    
    // Reload task data to sync worker_completions
    await loadTask()
    
    alert('Задача отмечена как выполненная!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка при отметке задачи')
  } finally {
    completing.value = false
  }
}

const approveTask = async () => {
  if (!confirm('Завершить задачу?')) return
  
  approving.value = true
  try {
    const authStore = useAuthStore()
    const userId = authStore.user?.id || 1
    await api.post(`/tasks/${route.params.id}/approve?user_id=${userId}`)
    
    // Reload task and history
    await loadTask()
    
    alert('Задача завершена!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка при завершении задачи')
  } finally {
    approving.value = false
  }
}

const reworkTask = async () => {
  if (!confirm('Вернуть задачу на доработку? Прогресс всех исполнителей будет сброшен.')) return
  
  reworking.value = true
  try {
    const authStore = useAuthStore()
    const userId = authStore.user?.id || 1
    await api.post(`/tasks/${route.params.id}/rework?user_id=${userId}`)
    
    // Reload task and history
    await loadTask()
    
    alert('Задача отправлена на доработку!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка при отправке на доработку')
  } finally {
    reworking.value = false
  }
}

const getWorkerName = (workerId) => {
  // Try to get worker name from assigned workers list
  const worker = assignedWorkers.value.find(w => w.id === workerId)
  if (worker) {
    return worker.full_name || worker.email
  }
  
  // Fallback to available workers or show ID
  const availWorker = availableWorkers.value.find(w => w.id === workerId)
  if (availWorker) {
    return availWorker.full_name || availWorker.email
  }
  
  return `Исполнитель #${workerId}`
}

const isWorkerCompleted = (workerId) => {
  return task.value?.worker_completions?.some(wc => wc.worker_id === workerId)
}

const handleUpdate = async () => {
  saving.value = true
  error.value = null

  try {
    await tasksStore.updateTask(route.params.id, form.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при обновлении'
  } finally {
    saving.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('Вы уверены, что хотите удалить эту задачу?')) return

  saving.value = true
  error.value = null

  try {
    await tasksStore.deleteTask(route.params.id)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при удалении'
  } finally {
    saving.value = false
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return

  commenting.value = true
  try {
    await commentsStore.addComment(route.params.id, newComment.value)
    newComment.value = ''
  } catch (err) {
    alert('Ошибка при добавлении комментария')
  } finally {
    commenting.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatHistoryEvent = (eventType) => {
  const map = {
    'created': 'Задача создана',
    'status_changed': 'Статус изменен',
    'assigned': 'Задача назначена',
    'comment_added': 'Комментарий добавлен',
    'worker_completed': 'Исполнитель отметил выполнение',
    'approved': 'Задача завершена',
    'returned': 'Возвращена на доработку'
  }
  return map[eventType] || eventType
}

const getHistoryIcon = (eventType) => {
  const icons = {
    'created': '',
    'status_changed': '',
    'assigned': '',
    'comment_added': '',
    'worker_completed': '',
    'approved': '',
    'returned': ''
  }
  return icons[eventType] || ''
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const getStatusBadgeClass = (status) => {
  const baseClass = 'inline-block px-3 py-1 rounded-full text-xs font-semibold'
  const classes = {
    'new': 'bg-red-100 text-red-800',
    'in_progress': 'bg-yellow-100 text-yellow-800',
    'completed': 'bg-green-100 text-green-800'
  }
  return `${baseClass} ${classes[status] || classes.new}`
}

const getPriorityBadgeClass = (priority) => {
  const baseClass = 'inline-block px-3 py-1 rounded-full text-xs font-semibold'
  const classes = {
    'low': 'bg-orange-100 text-orange-800',
    'medium': 'bg-purple-100 text-purple-800',
    'high': 'bg-orange-100 text-orange-800',
    'urgent': 'bg-red-100 text-red-800'
  }
  return `${baseClass} ${classes[priority] || classes.medium}`
}

const formatStatus = (status) => {
  const map = {
    'new': 'Новая',
    'in_progress': 'В процессе',
    'completed': 'Завершена'
  }
  return map[status] || status
}

const formatPriority = (priority) => {
  const map = {
    'low': 'Низкий',
    'medium': 'Средний',
    'high': 'Высокий',
    'urgent': 'Срочный'
  }
  return map[priority] || priority
}

onMounted(loadTask)
</script>
