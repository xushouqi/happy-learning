<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4 flex flex-col items-center">
    <header class="w-full max-w-2xl flex items-center justify-between mb-6">
      <button @click="router.push('/courses')" class="text-3xl hover:scale-110 transition-transform">←</button>
      <h1 class="text-xl font-bold text-primary">课程详情</h1>
      <span class="text-2xl">⭐ {{ course?.total_stars || 0 }}</span>
    </header>

    <div v-if="loading" class="bg-white rounded-2xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-3xl mb-3 animate-bounce">📖</p>
      <p class="text-xl text-gray-600">加载中…</p>
    </div>

    <div v-else-if="course" class="w-full max-w-2xl">
      <!-- 课程信息 -->
      <div class="bg-white rounded-3xl p-6 shadow-lg mb-6 text-center">
        <p class="text-6xl mb-3">{{ course.cover_emoji || '📚' }}</p>
        <h2 class="text-2xl font-bold text-gray-800 mb-2">{{ course.title }}</h2>
        <p v-if="course.textbook_name" class="text-sm text-gray-500 mb-1">{{ course.textbook_name }} · {{ course.unit_name }}</p>
        <p class="text-gray-600 text-base mb-4">{{ course.description }}</p>
        <!-- 进度条 -->
        <div class="bg-gray-200 rounded-full h-3 mb-1">
          <div class="bg-secondary h-3 rounded-full transition-all" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <p class="text-sm text-gray-500">已完成 {{ course.completed_lessons }} / {{ course.lesson_count }} 节课</p>
      </div>

      <!-- 课时列表 -->
      <h3 class="text-lg font-bold text-gray-800 mb-3 px-1">课时列表</h3>
      <div class="space-y-3">
        <div
          v-for="(lesson, idx) in course.lessons"
          :key="lesson.id"
          :class="[
            'bg-white rounded-2xl p-5 shadow-md flex items-center gap-4 transition-all',
            isOpen(lesson, idx) ? 'cursor-pointer hover:shadow-lg' : 'opacity-60',
          ]"
          @click="openLesson(lesson, idx)"
        >
          <div class="w-12 h-12 rounded-2xl bg-pink-100 flex items-center justify-center text-2xl shrink-0">
            {{ lesson.completed ? '✅' : (isOpen(lesson, idx) ? '🚀' : '🔒') }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-bold text-gray-800">{{ idx + 1 }}. {{ lesson.title }}</span>
              <span v-if="lesson.completed" class="text-xs text-green-600 bg-green-50 rounded-full px-2 py-0.5 whitespace-nowrap">
                ⭐ {{ lesson.stars }}
              </span>
            </div>
            <p class="text-sm text-gray-500 mt-0.5">{{ lesson.subtitle }}</p>
            <p v-if="!isOpen(lesson, idx) && !lesson.completed" class="text-xs text-gray-400 mt-1">
              先完成上一节课就能解锁哦
            </p>
          </div>
          <span class="text-2xl text-gray-300">›</span>
        </div>
      </div>

      <div class="text-center mt-8">
        <button @click="router.push('/dashboard')" class="px-6 py-3 bg-gray-100 text-gray-600 rounded-full text-base font-semibold hover:bg-gray-200 transition-all">
          返回首页
        </button>
      </div>
    </div>

    <div v-else class="bg-white rounded-2xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-3xl mb-3">😵</p>
      <p class="text-xl text-gray-600">课程加载失败</p>
      <button @click="router.push('/courses')" class="mt-4 px-6 py-3 bg-primary text-white rounded-full text-lg">返回课程列表</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { courseApi } from '../api'

const router = useRouter()
const route = useRoute()

const course = ref(null)
const loading = ref(true)

const getUserId = () => parseInt(localStorage.getItem('userId'))

const progressPercent = computed(() => {
  if (!course.value?.lesson_count) return 0
  return Math.round((course.value.completed_lessons / course.value.lesson_count) * 100)
})

const lessonIndex = (lesson) => course.value?.lessons.findIndex((l) => l.id === lesson.id) || 0

// 第一课或上一课已完成 → 可上课;已完成的课可随时复习
const isOpen = (lesson, idx) => {
  if (lesson.completed) return true
  if (idx === 0) return true
  const prev = course.value?.lessons[idx - 1]
  return !!prev?.completed
}

const openLesson = (lesson, idx) => {
  if (!isOpen(lesson, idx)) return
  router.push(`/courses/${course.value.id}/lesson/${lesson.id}`)
}

onMounted(async () => {
  try {
    const res = await courseApi.get(route.params.courseId, getUserId())
    course.value = res.data
  } catch {
    course.value = null
  } finally {
    loading.value = false
  }
})
</script>
