<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4 flex flex-col items-center">
    <header class="w-full max-w-2xl flex items-center justify-between mb-6">
      <button @click="router.push('/dashboard')" class="text-3xl hover:scale-110 transition-transform">←</button>
      <h1 class="text-xl font-bold text-primary">{{ headerTitle }}</h1>
      <span class="text-sm text-gray-600">边玩边学</span>
    </header>

    <div v-if="loading" class="bg-white rounded-2xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-3xl mb-3 animate-bounce">🎒</p>
      <p class="text-xl text-gray-600">加载中…</p>
    </div>

    <template v-else-if="courses.length">
      <!-- 教材切换导航(有 filter 时显示返回全部) -->
      <div v-if="filterTextbookId" class="w-full max-w-2xl mb-4">
        <button @click="clearFilter" class="text-sm text-gray-500 bg-white rounded-full px-4 py-2 shadow-sm hover:bg-gray-50 transition-all">
          ← 查看全部课程
        </button>
      </div>

      <!-- 按教材分组 -->
      <div v-for="group in groupedCourses" :key="group.textbook_id" class="w-full max-w-2xl mb-6">
        <!-- 教材组标题(无 filter 时展示) -->
        <div v-if="!filterTextbookId" class="flex items-center justify-between mb-3 px-1">
          <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2">
            <span>{{ group.icon }}</span>
            {{ group.textbook_name }}
          </h2>
          <span class="text-sm text-gray-500">
            已完成 {{ group.completed }} / {{ group.total }} 节
            <span class="text-amber-500 font-semibold ml-1">⭐ {{ group.stars }}</span>
          </span>
        </div>

        <div class="space-y-3">
          <div
            v-for="c in group.courses"
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
                <p v-if="c.unit_name" class="text-xs text-gray-500">{{ c.unit_name }}</p>
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
      </div>
    </template>

    <div v-else class="bg-white rounded-2xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-3xl mb-3">🌱</p>
      <p class="text-xl text-gray-600">还没有互动课程,敬请期待!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { courseApi } from '../api'

const router = useRouter()
const route = useRoute()
const courses = ref([])
const loading = ref(true)

const getUserId = () => parseInt(localStorage.getItem('userId'))

// 教材图标映射(按 textbook_id;无则用课程 emoji)
const textbookIcons = {
  2: '🔤', // Oxford Phonics World
  3: '🐻', // Big Muzzy
}

// 当前筛选的教材 id(来自 ?textbook=)
const filterTextbookId = computed(() => {
  const v = parseInt(route.query.textbook)
  return Number.isInteger(v) ? v : null
})

const headerTitle = computed(() => {
  if (!filterTextbookId.value) return '互动课程'
  const g = groupedCourses.value.find((x) => x.textbook_id === filterTextbookId.value)
  return g ? g.textbook_name : '互动课程'
})

// 按教材分组
const groupedCourses = computed(() => {
  const map = new Map()
  for (const c of courses.value) {
    if (filterTextbookId.value && c.textbook_id !== filterTextbookId.value) continue
    if (!map.has(c.textbook_id)) {
      map.set(c.textbook_id, {
        textbook_id: c.textbook_id,
        textbook_name: c.textbook_name || '课程',
        icon: textbookIcons[c.textbook_id] || c.cover_emoji || '📚',
        courses: [],
        completed: 0,
        total: 0,
        stars: 0,
      })
    }
    const g = map.get(c.textbook_id)
    g.courses.push(c)
    g.completed += c.completed_lessons || 0
    g.total += c.lesson_count || 0
    g.stars += c.total_stars || 0
  }
  return [...map.values()]
})

const percent = (c) => {
  if (!c.lesson_count) return 0
  return Math.round((c.completed_lessons / c.lesson_count) * 100)
}

const openCourse = (c) => {
  router.push(`/courses/${c.id}`)
}

const clearFilter = () => {
  router.push('/courses')
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
