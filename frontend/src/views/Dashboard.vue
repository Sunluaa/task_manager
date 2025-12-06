<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <nav class="bg-white shadow">
      <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-blue-600">Задачи</h1>
        <div class="flex items-center gap-4">
          <span v-if="authStore.user" class="text-sm text-gray-600">
            {{ authStore.user.email }}
          </span>
          <router-link
            v-if="authStore.user?.role === 'admin'"
            to="/admin/users"
            class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-semibold"
          >
            Пользователи
          </router-link>
          <button
            @click="handleLogout"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition font-semibold"
          >
            Выход
          </button>
        </div>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto px-4 py-8">
      <div class="flex justify-between items-center mb-8">
        <h2 class="text-3xl font-bold text-gray-900">Мои задачи</h2>
        <router-link
          v-if="authStore.user?.role === 'admin'"
          to="/tasks/new"
          class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
        >
          + Новая задача
        </router-link>
      </div>

      <div class="flex gap-3 mb-8 flex-wrap">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="currentFilter = filter.value"
          :class="[
            'px-4 py-2 rounded-lg font-semibold transition',
            currentFilter === filter.value
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
          ]"
        >
          {{ filter.label }} ({{ getFilterCount(filter.value) }})
        </button>
      </div>

      <div v-if="tasksStore.loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="filteredTasks.length === 0" class="text-center py-12">
        <p v-if="authStore.user?.role === 'admin'" class="text-gray-600">Нет задач. Создайте первую!</p>
        <p v-else class="text-gray-600">Вам не назначены задачи.</p>
      </div>

      <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition cursor-pointer relative"
          @click="goToTask(task.id)"
        >
          <!-- Checkbox for workers (non-clickable on card, clickable on itself) -->
          <div v-if="authStore.user?.role === 'user'" class="absolute top-4 right-4">
            <label class="flex items-center gap-2 cursor-pointer" @click.stop="toggleTaskComplete(task.id)">
              <input
                type="checkbox"
                :checked="isTaskCompletedByWorker(task.id)"
                class="w-5 h-5 rounded cursor-pointer"
              />
              <span class="text-xs text-gray-600">Выполнено</span>
            </label>
          </div>

          <h3 class="font-semibold text-lg text-gray-900 pr-16">{{ task.title }}</h3>
          <p class="text-gray-600 text-sm mt-2 line-clamp-2">{{ task.description }}</p>
          <div class="flex gap-2 mt-4">
            <span :class="getStatusBadgeClass(task.status)">
              {{ formatStatus(task.status) }}
            </span>
            <span :class="getPriorityBadgeClass(task.priority)">
              {{ formatPriority(task.priority) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTasksStore } from '../stores/tasks'

const router = useRouter()
const authStore = useAuthStore()
const tasksStore = useTasksStore()

const currentFilter = ref('all')

const adminFilters = [
  { label: 'Все', value: 'all' },
  { label: 'Новые', value: 'new' },
  { label: 'В процессе', value: 'in_progress' },
  { label: 'Готовые', value: 'completed' }
]

const userFilters = [
  { label: 'Невыполненные', value: 'incomplete' },
  { label: 'Выполненные', value: 'completed' }
]

const filters = computed(() => {
  return authStore.user?.role === 'admin' ? adminFilters : userFilters
})

const filteredTasks = computed(() => {
  if (!Array.isArray(tasksStore.tasks)) return []
  
  // For regular users/workers - show only assigned tasks
  if (authStore.user?.role === 'user') {
    let workerTasks = tasksStore.tasks.filter(task => 
      task.worker_ids && task.worker_ids.includes(authStore.user?.id)
    )
    
    // Filter by completion status
    if (currentFilter.value === 'incomplete') {
      return workerTasks.filter(task => !isTaskCompletedByWorker(task.id))
    }
    if (currentFilter.value === 'completed') {
      return workerTasks.filter(task => isTaskCompletedByWorker(task.id))
    }
    
    return workerTasks
  }
  
  // For admins - show all tasks
  if (currentFilter.value === 'all') return tasksStore.tasks
  return tasksStore.tasks.filter(task => task.status === currentFilter.value)
})

const getFilterCount = (filter) => {
  if (!Array.isArray(tasksStore.tasks)) return 0
  
  // For users - count by completion status
  if (authStore.user?.role === 'user') {
    let workerTasks = tasksStore.tasks.filter(task => 
      task.worker_ids && task.worker_ids.includes(authStore.user?.id)
    )
    
    if (filter === 'incomplete') {
      return workerTasks.filter(task => !isTaskCompletedByWorker(task.id)).length
    }
    if (filter === 'completed') {
      return workerTasks.filter(task => isTaskCompletedByWorker(task.id)).length
    }
    return workerTasks.length
  }
  
  // For admins - count by status
  if (filter === 'all') return tasksStore.tasks.length
  return tasksStore.tasks.filter(task => task.status === filter).length
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
    'low': 'bg-blue-100 text-blue-800',
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

const goToTask = (id) => {
  router.push(`/tasks/${id}`)
}

const handleLogout = () => {
  authStore.logout()
  tasksStore.clearTasks()
  router.push('/login')
}

const loadTasks = async () => {
  await tasksStore.fetchTasks()
}

const isTaskCompletedByWorker = (taskId) => {
  const task = tasksStore.tasks.find(t => t.id === taskId)
  if (!task || !task.worker_completions) return false
  return task.worker_completions.some(wc => wc.worker_id === authStore.user?.id)
}

const toggleTaskComplete = async (taskId) => {
  try {
    if (isTaskCompletedByWorker(taskId)) {
      // Already completed - do nothing or show message
      return
    }
    
    // Mark as completed
    await tasksStore.completeTaskByWorker(taskId)
    
    // Reload tasks to update UI
    await loadTasks()
  } catch (err) {
    console.error('Failed to complete task:', err)
    alert('Ошибка при отметке задачи')
  }
}

onMounted(loadTasks)
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
