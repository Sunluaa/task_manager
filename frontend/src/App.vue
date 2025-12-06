<template>
  <div class="min-h-screen bg-gray-100">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.token) {
    const isValid = await authStore.checkAuth()
    if (!isValid) {
      router.push('/login')
    }
  }
})
</script>

<style scoped>
</style>
