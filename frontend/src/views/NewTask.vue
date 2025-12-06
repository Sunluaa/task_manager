<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <nav class="bg-white shadow">
      <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <router-link to="/" class="text-2xl font-bold text-blue-600">Задачи</router-link>
        <button @click="handleLogout" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition">
          Выход
        </button>
      </div>
    </nav>

    <div class="max-w-2xl mx-auto px-4 py-8">
      <h2 class="text-3xl font-bold text-gray-900 mb-8">Создать новую задачу</h2>

      <div class="bg-white rounded-lg shadow-md p-8">
        <form @submit.prevent="handleCreate" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Название *</label>
            <input
              v-model="form.title"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Название задачи"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Описание</label>
            <textarea
              v-model="form.description"
              rows="4"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Описание задачи"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Приоритет</label>
              <select
                v-model="form.priority"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
                <option value="urgent">Срочный</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Статус</label>
              <select
                v-model="form.status"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="new">Новая</option>
                <option value="in_progress">В процессе</option>
                <option value="completed">Завершена</option>
              </select>
            </div>
          </div>

          <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-800 text-sm">{{ error }}</p>
          </div>

          <div class="flex gap-4">
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ loading ? 'Создание...' : 'Создать' }}
            </button>
            <router-link
              to="/"
              class="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-900 font-semibold py-2 rounded-lg text-center transition"
            >
              Отмена
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTasksStore } from '../stores/tasks'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const tasksStore = useTasksStore()
const authStore = useAuthStore()

const form = ref({
  title: '',
  description: '',
  priority: 'medium',
  status: 'new'
})

const loading = ref(false)
const error = ref(null)

const handleCreate = async () => {
  if (!form.value.title.trim()) {
    error.value = 'Название обязательно'
    return
  }

  loading.value = true
  error.value = null

  try {
    await tasksStore.createTask(form.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при создании задачи'
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
