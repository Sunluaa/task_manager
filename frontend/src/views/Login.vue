<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <div class="mb-8 text-center">
          <h1 class="text-4xl font-bold text-blue-600 mb-2"></h1>
          <h2 class="text-2xl font-bold text-gray-900">Менеджер задач</h2>
          <p class="text-gray-600 text-sm mt-2">Войдите для управления задачами</p>
        </div>

        <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-800 text-sm">{{ error }}</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              v-model="email"
              type="email"
              required
              :disabled="loading"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              placeholder="admin@admin.admin"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Пароль</label>
            <input
              v-model="password"
              type="password"
              required
              :disabled="loading"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            :disabled="loading || !email || !password"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Вход...' : 'Войти' }}
          </button>
        </form>

        <div class="mt-6 pt-6 border-t border-gray-200">
          <p class="text-xs text-gray-500 text-center">
            Демо: admin@admin.admin / admin
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('admin@admin.admin')
const password = ref('admin')
const loading = ref(false)
const error = ref(null)

const handleLogin = async () => {
  loading.value = true
  error.value = null
  try {
    await authStore.login(email.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
