<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4 flex flex-col items-center">
    <header class="w-full max-w-2xl flex items-center justify-between mb-6">
      <button @click="router.push('/dashboard')" class="text-3xl hover:scale-110 transition-transform">←</button>
      <h1 class="text-xl font-bold text-primary">互动课程</h1>
      <span class="text-sm text-gray-600">边玩边学</span>
    </header>

    <div v-if="loading" class="bg-white rounded-2xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-3xl mb-3 animate-bounce">🎒</p>
      <p class="text-xl text-gray-600">加载中…</p>
    </div>

    <div v-else-if="courses.length" class="w-full max-w-2xl space-y-4">
      <div
        v-for="c in courses"
        :key="c.id"
        class="bg-white rounded-3xl p-6 shadow-md cursor-pointer hover:shadow-lg transition-all"
        @click="openCourse(c)"
      >
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-b from-amber-100 to-pink-100 flex items-center justify-center text-4xl shrink-0">
            {{ c.cover_emoji || '📚' }}
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-xl font-bold text-gray-800">{{ c.title }}</h2>
            <p v-if="c.textbook_name" class="text-xs text-gray-500">{{ c.textbook_name }} · {{ c.unit_name }}</p>
            <p class="text-sm text-gray-500 mt-0.5 line-clamp-1">{{ c.description }}</p>
          </div>
          <span class="text-2xl text-gray-300">›</span>
        </div>
        <!-- 进度 -->
        <div class="mt-3 flex items-center gap-3">
          <div class="flex-1 bg-gray-200 rounded-full h-2.5">
            <div class="bg-secondary h-2.5 rounded-full transition-all" :style="{ width: percent(c) + '%' }"></div>
          </div>
          <span class="text-sm text-gray-500 whitespace-nowrap">
            {{ c.completed_lessons }}/{{ c.lesson_count }} 节
          </span>
          <span class="text-sm text-amber-500 font-semibold whitespace-nowrap">⭐ {{ c.total_stars }}</span>
        </div>
      </div>
    </div>

    <div v-else class="bg-white rounded-2xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-3xl mb-3">🌱</p>
      <p class="text-xl text-gray-600">还没有互动课程,敬请期待!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { courseApi } from '../api'

const router = useRouter()
const courses = ref([])
const loading = ref(true)

const getUserId = () => parseInt(localStorage.getItem('userId'))

const percent = (c) => {
  if (!c.lesson_count) return 0
  return Math.round((c.completed_lessons / c.lesson_count) * 100)
}

const openCourse = (c) => {
  router.push(`/courses/${c.id}`)
}

onMounted(async () => {
  try {
    const res = await courseApi.list(getUserId())
    courses.value = res.data
  } catch {
    courses.value = []
  } finally {
    loading.value = false
  }
})
</script>
