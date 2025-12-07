<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 to-orange-100 p-8">
    <div class="max-w-6xl mx-auto">
      <div class="flex justify-between items-center mb-8">
        <div class="flex items-center gap-4">
          <router-link
            to="/"
            class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-semibold transition"
          >
            ← Панель
          </router-link>
          <h1 class="text-4xl font-bold text-gray-800">Управление пользователями</h1>
        </div>
        <button
          @click="showCreateModal = true"
          class="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg font-semibold transition"
        >
          Новый пользователь
        </button>
      </div>

      <!-- Users Table -->
      <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div v-if="usersStore.loading" class="p-8 text-center">
          <p class="text-gray-500">Загрузка пользователей...</p>
        </div>
        <div v-else-if="usersStore.users.length === 0" class="p-8 text-center">
          <p class="text-gray-500">Пользователи не найдены</p>
        </div>
        <table v-else class="w-full">
          <thead class="bg-gray-100 border-b">
            <tr>
              <th class="px-6 py-3 text-left text-gray-700 font-semibold">Email</th>
              <th class="px-6 py-3 text-left text-gray-700 font-semibold">Имя</th>
              <th class="px-6 py-3 text-left text-gray-700 font-semibold">Роль</th>
              <th class="px-6 py-3 text-left text-gray-700 font-semibold">Статус</th>
              <th class="px-6 py-3 text-left text-gray-700 font-semibold">Создан</th>
              <th class="px-6 py-3 text-right text-gray-700 font-semibold">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in usersStore.users" :key="user.id" class="border-b hover:bg-gray-50 transition">
              <td class="px-6 py-4 text-gray-800">{{ user.email }}</td>
              <td class="px-6 py-4 text-gray-800">{{ user.full_name || '-' }}</td>
              <td class="px-6 py-4">
                <span :class="['px-3 py-1 rounded-full text-sm font-semibold', user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-orange-100 text-orange-800']">
                  {{ user.role === 'admin' ? 'Администратор' : 'Пользователь' }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span :class="['px-3 py-1 rounded-full text-sm font-semibold', user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800']">
                  {{ user.is_active ? 'Активен' : 'Неактивен' }}
                </span>
              </td>
              <td class="px-6 py-4 text-gray-600 text-sm">{{ formatDate(user.created_at) }}</td>
              <td class="px-6 py-4 text-right">
                <button @click="editUser(user)" class="text-orange-600 hover:text-orange-800 font-semibold mr-4 transition">
                  Редактировать
                </button>
                <button
                  @click="confirmDelete(user)"
                  :disabled="user.id === authStore.user?.id"
                  :class="['font-semibold transition', user.id === authStore.user?.id ? 'text-gray-400 cursor-not-allowed' : 'text-red-600 hover:text-red-800']"
                >
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" @click.self="closeModal">
      <div class="bg-white rounded-lg shadow-2xl max-w-md w-full p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">
          {{ editingUser ? 'Редактировать пользователя' : 'Создать пользователя' }}
        </h2>

        <div class="space-y-4">
          <div>
            <label class="block text-gray-700 font-semibold mb-2">Email *</label>
            <input
              v-model="formData.email"
              :disabled="!!editingUser"
              type="email"
              :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:bg-gray-100', emailError ? 'border-red-500' : 'border-gray-300']"
              placeholder="user@example.com"
            />
            <p v-if="emailError" class="text-red-500 text-sm mt-1">{{ emailError }}</p>
          </div>

          <div v-if="!editingUser">
            <label class="block text-gray-700 font-semibold mb-2">Пароль *</label>
            <input
              v-model="formData.password"
              type="password"
              :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500', passwordError ? 'border-red-500' : 'border-gray-300']"
              placeholder="Минимум 6 символов"
            />
            <p v-if="passwordError" class="text-red-500 text-sm mt-1">{{ passwordError }}</p>
          </div>

          <div>
            <label class="block text-gray-700 font-semibold mb-2">Имя *</label>
            <input
              v-model="formData.full_name"
              type="text"
              :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500', fullNameError ? 'border-red-500' : 'border-gray-300']"
              placeholder="Иван Иванов"
            />
            <p v-if="fullNameError" class="text-red-500 text-sm mt-1">{{ fullNameError }}</p>
          </div>

          <div>
            <label class="block text-gray-700 font-semibold mb-2">Роль</label>
            <select v-model="formData.role" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500">
              <option value="user">Пользователь</option>
              <option value="admin">Администратор</option>
            </select>
          </div>

          <div>
            <label class="flex items-center">
              <input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-orange-600 rounded focus:ring-2 focus:ring-orange-500" />
              <span class="ml-2 text-gray-700 font-semibold">Активен</span>
            </label>
          </div>

          <div v-if="formError" class="p-3 bg-red-100 border border-red-300 rounded text-red-700">
            {{ formError }}
          </div>
        </div>

        <div class="mt-6 flex justify-end space-x-3">
          <button @click="closeModal" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-semibold transition">
            Отмена
          </button>
          <button
            @click="saveUser"
            :disabled="isSaving || !isFormValid"
            :class="['px-4 py-2 rounded-lg font-semibold transition text-white', isFormValid ? 'bg-orange-600 hover:bg-orange-700' : 'bg-gray-400 cursor-not-allowed']"
          >
            {{ isSaving ? 'Сохранение...' : editingUser ? 'Обновить' : 'Создать' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" @click.self="showDeleteConfirm = false">
      <div class="bg-white rounded-lg shadow-2xl max-w-md w-full p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Подтверждение удаления</h2>
        <p class="text-gray-600 mb-6">
          Вы уверены, что хотите удалить пользователя <strong>{{ userToDelete?.email }}</strong
          >? Это действие нельзя отменить.
        </p>

        <div class="flex justify-end space-x-3">
          <button @click="showDeleteConfirm = false" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-semibold transition">
            Отмена
          </button>
          <button @click="deleteUser" :disabled="isDeleting" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition disabled:bg-red-400">
            {{ isDeleting ? 'Удаление...' : 'Удалить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useUsersStore } from '../../stores/users'

const authStore = useAuthStore()
const usersStore = useUsersStore()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)
const editingUser = ref(null)
const userToDelete = ref(null)
const isSaving = ref(false)
const isDeleting = ref(false)
const formError = ref('')

const formData = ref({
  email: '',
  password: '',
  full_name: '',
  role: 'user',
  is_active: true
})

const emailError = ref('')
const passwordError = ref('')
const fullNameError = ref('')

const isFormValid = computed(() => {
  return !emailError.value && !passwordError.value && !fullNameError.value && formData.value.email && formData.value.full_name && (editingUser.value || formData.value.password)
})

const validateForm = () => {
  emailError.value = ''
  passwordError.value = ''
  fullNameError.value = ''

  if (!formData.value.email) {
    emailError.value = 'Email обязателен'
  } else if (!isValidEmail(formData.value.email)) {
    emailError.value = 'Некорректный email'
  }

  if (!editingUser.value) {
    if (!formData.value.password) {
      passwordError.value = 'Пароль обязателен'
    } else if (formData.value.password.length < 6) {
      passwordError.value = 'Пароль должен быть минимум 6 символов'
    }
  }

  if (!formData.value.full_name) {
    fullNameError.value = 'Имя обязательно'
  } else if (formData.value.full_name.trim().length < 2) {
    fullNameError.value = 'Имя должно быть минимум 2 символа'
  }
}

const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

watch([() => formData.value.email, () => formData.value.password, () => formData.value.full_name], () => {
  validateForm()
})

onMounted(() => {
  usersStore.fetchUsers()
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const editUser = (user) => {
  editingUser.value = user
  formData.value = {
    email: user.email,
    password: '',
    full_name: user.full_name || '',
    role: user.role,
    is_active: user.is_active
  }
  formError.value = ''
  emailError.value = ''
  passwordError.value = ''
  fullNameError.value = ''
  showEditModal.value = true
}

const confirmDelete = (user) => {
  userToDelete.value = user
  showDeleteConfirm.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingUser.value = null
  formData.value = {
    email: '',
    password: '',
    full_name: '',
    role: 'user',
    is_active: true
  }
  formError.value = ''
  emailError.value = ''
  passwordError.value = ''
  fullNameError.value = ''
}

const saveUser = async () => {
  validateForm()
  
  if (!isFormValid.value) {
    return
  }

  isSaving.value = true
  try {
    if (editingUser.value) {
      await usersStore.updateUser(editingUser.value.id, {
        full_name: formData.value.full_name,
        role: formData.value.role,
        is_active: formData.value.is_active
      })
    } else {
      await usersStore.createUser({
        email: formData.value.email,
        password: formData.value.password,
        full_name: formData.value.full_name,
        role: formData.value.role,
        is_active: formData.value.is_active
      })
    }
    await usersStore.fetchUsers()
    closeModal()
  } catch (error) {
    formError.value = error.response?.data?.detail || 'Ошибка при сохранении'
  } finally {
    isSaving.value = false
  }
}

const deleteUser = async () => {
  isDeleting.value = true
  try {
    await usersStore.deleteUser(userToDelete.value.id)
    await usersStore.fetchUsers()
    showDeleteConfirm.value = false
    userToDelete.value = null
  } catch (error) {
    alert(error.response?.data?.detail || 'Ошибка при удалении')
  } finally {
    isDeleting.value = false
  }
}
</script>
