<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4">
    <header class="flex items-center justify-between mb-6">
      <button @click="router.push('/')" class="text-3xl hover:scale-110 transition-transform">🏠</button>
      <h1 class="text-2xl font-bold text-primary">{{ greeting }}</h1>
      <div class="flex gap-3">
        <button @click="router.push('/courses')" class="flex flex-col items-center hover:scale-110 transition-transform">
          <span class="text-3xl">🎓</span>
          <span class="text-xs text-gray-600">课程</span>
        </button>
        <button @click="router.push('/wrongbook')" class="flex flex-col items-center hover:scale-110 transition-transform relative">
          <span class="text-3xl">📝</span>
          <span class="text-xs text-gray-600">错题</span>
          <span v-if="wrongCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">{{ wrongCount }}</span>
        </button>
        <button @click="router.push('/calendar')" class="flex flex-col items-center hover:scale-110 transition-transform">
          <span class="text-3xl">📅</span>
          <span class="text-xs text-gray-600">日历</span>
        </button>
        <button @click="router.push('/progress')" class="flex flex-col items-center hover:scale-110 transition-transform">
          <span class="text-3xl">📊</span>
          <span class="text-xs text-gray-600">进度</span>
        </button>
      </div>
    </header>

    <!-- 互动课程入口(按教材分组) -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-xl font-bold text-gray-800">互动课程</h2>
        <button @click="router.push('/courses')" class="text-sm text-primary font-semibold hover:underline">
          全部课程 ›
        </button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="tb in courseTextbooks"
          :key="tb.textbook_id"
          class="bg-white rounded-2xl p-5 shadow-md cursor-pointer hover:shadow-lg transition-all border-2 border-primary/30"
          @click="router.push('/courses?textbook=' + tb.textbook_id)"
        >
          <div class="flex items-center gap-4">
            <span class="text-4xl">{{ tb.icon }}</span>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-bold text-gray-800">{{ tb.textbook_name }}</h3>
              <p class="text-sm text-gray-500 mt-0.5">已完成 {{ tb.completed }} / {{ tb.total }} 节课</p>
            </div>
            <span class="text-2xl text-gray-300">›</span>
          </div>
          <div class="mt-3 bg-gray-200 rounded-full h-2.5">
            <div class="bg-secondary h-2.5 rounded-full transition-all" :style="{ width: tb.percent + '%' }"></div>
          </div>
          <div class="mt-2 flex items-center justify-between">
            <span class="text-xs text-gray-400">{{ tb.course_count }} 门课程</span>
            <span class="text-sm text-amber-500 font-semibold">⭐ {{ tb.stars }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Today's Challenge -->
    <div class="bg-white rounded-2xl p-6 shadow-lg mb-6 border-4 border-accent">
      <h2 class="text-xl font-bold text-gray-800 mb-2">今日挑战</h2>
      <p class="text-gray-600 mb-4">完成一个单元的学习，赢取星星吧！</p>
      <button
        v-if="recommendedUnit"
        @click="startUnit(recommendedUnit)"
        class="px-6 py-3 bg-primary text-white rounded-full text-lg hover:bg-opacity-80 transition-all animate-pulse"
      >
        开始学习 →
      </button>
    </div>

    <!-- Textbook Cards -->
    <h2 class="text-xl font-bold text-gray-800 mb-4">选择教材</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="book in textbookList"
        :key="book.id"
        class="bg-white rounded-2xl p-5 shadow-md hover:shadow-lg transition-all cursor-pointer"
        @click="selectTextbook(book)"
      >
        <div class="text-4xl mb-3">{{ textbookIcons[book.id] || '📚' }}</div>
        <h3 class="text-lg font-bold text-gray-800">{{ book.name }}</h3>
        <p class="text-sm text-gray-500 mt-1">{{ book.units?.length || 0 }} 个单元</p>
        <!-- Progress bar -->
        <div class="mt-3 bg-gray-200 rounded-full h-2">
          <div
            class="bg-secondary h-2 rounded-full transition-all"
            :style="{ width: getProgressPercent(book.id) + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Textbook Detail Modal -->
    <div v-if="selectedBook" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 m-4 max-w-md w-full max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold text-gray-800">{{ selectedBook.name }}</h2>
          <button @click="selectedBook = null" class="text-2xl">✕</button>
        </div>
        <div class="space-y-3">
          <div
            v-for="unit in selectedBook.units"
            :key="unit.id"
            class="w-full flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-accent/30 transition-all group"
          >
            <button @click="startUnit(unit)" class="flex-1 text-left">
              <span class="font-semibold text-gray-700">{{ unit.name }}</span>
              <span v-if="unit.completed" class="text-xs text-green-600 ml-2">✓ {{ unit.best_score }}/{{ unit.total_questions }}</span>
            </button>
            <button
              v-if="unit.completed || unit.attempts > 0"
              @click="clearUnit(unit.id)"
              class="text-red-400 hover:text-red-600 bg-red-50 hover:bg-red-100 rounded-full px-2 py-1 text-xs transition-colors"
              title="清空学习记录"
            >
              清空
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { textbooks as textbooksApi, progress as progressApi, scores as scoresApi, courseApi } from '../api'

const router = useRouter()
const textbookList = ref([])
const selectedBook = ref(null)
const progressData = ref([])
const userProgress = ref([])
const wrongCount = ref(0)
const courseList = ref([])

const currentUser = computed(() => {
  const id = localStorage.getItem('userId')
  const name = localStorage.getItem('userName')
  return id ? { id, name, avatar: '🌟' } : null
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好！'
  if (hour < 18) return '下午好！'
  return '晚上好！'
})

const textbookIcons = {
  2: '🔤',  // Oxford Phonics World
  3: '🐻',  // Big Muzzy
}

// 互动课程:按教材分组的入口卡片
const courseTextbooks = computed(() => {
  const map = new Map()
  for (const c of courseList.value) {
    if (!map.has(c.textbook_id)) {
      map.set(c.textbook_id, {
        textbook_id: c.textbook_id,
        textbook_name: c.textbook_name || '课程',
        icon: textbookIcons[c.textbook_id] || c.cover_emoji || '📚',
        course_count: 0,
        completed: 0,
        total: 0,
        stars: 0,
        percent: 0,
      })
    }
    const g = map.get(c.textbook_id)
    g.course_count++
    g.completed += c.completed_lessons || 0
    g.total += c.lesson_count || 0
    g.stars += c.total_stars || 0
  }
  for (const g of map.values()) {
    g.percent = g.total ? Math.round((g.completed / g.total) * 100) : 0
  }
  return [...map.values()]
})

const recommendedUnit = computed(() => {
  if (textbookList.value.length > 0 && textbookList.value[0].units?.length > 0) {
    return textbookList.value[0].units[0]
  }
  return null
})

onMounted(async () => {
  try {
    const res = await textbooksApi.list()
    textbookList.value = res.data
  } catch {
    textbookList.value = []
  }

  // 互动课程列表(按教材分组展示入口)
  try {
    const res = await courseApi.list(currentUser.value?.id)
    courseList.value = res.data
  } catch {
    courseList.value = []
  }

  if (currentUser.value?.id) {
    try {
      const [dailyRes, courseRes] = await Promise.all([
        progressApi.byUser(currentUser.value.id),
        progressApi.byCourse(currentUser.value.id),
      ])
      progressData.value = dailyRes.data
      userProgress.value = courseRes.data
    } catch {
      try {
        const res = await progressApi.byUser(currentUser.value.id)
        progressData.value = res.data
      } catch {}
    }

    try {
      const res = await scoresApi.wrongQuestions(currentUser.value.id)
      wrongCount.value = res.data?.length || 0
    } catch {}
  }
})

const getProgressPercent = (bookId) => {
  const bookProgress = userProgress.value.find(c => c.id === bookId)
  if (bookProgress) {
    return bookProgress.total_units ? Math.round(bookProgress.completed_units / bookProgress.total_units * 100) : 0
  }
  const book = textbookList.value.find(c => c.id === bookId)
  if (!book?.units?.length) return 0
  const completed = progressData.value.filter(p =>
    book.units.some(u => u.id === p.unit_id) && p.completed
  ).length
  return Math.round((completed / book.units.length) * 100)
}

const selectTextbook = (book) => {
  // Merge progress data into unit objects
  const bookProgress = userProgress.value.find(c => c.id === book.id)
  const enrichedBook = { ...book, units: book.units.map(u => {
    const up = bookProgress?.units?.find(pu => pu.id === u.id)
    return up ? { ...u, ...up } : { ...u, completed: false, best_score: 0, total_questions: 0, attempts: 0 }
  })}
  selectedBook.value = enrichedBook
}

const startUnit = (unit) => {
  router.push(`/quiz-type/${unit.id}`)
}

const clearUnit = async (unitId) => {
  if (!confirm('确定要清空该单元的学习记录吗？')) return
  try {
    await scoresApi.clearUnit(currentUser.value.id, unitId)
    // Reload textbook list and selected book to reflect cleared progress
    const [res, courseRes] = await Promise.all([
      textbooksApi.list(),
      progressApi.byCourse(currentUser.value.id),
    ])
    textbookList.value = res.data
    userProgress.value = courseRes.data
    // Update selectedBook if open
    if (selectedBook.value) {
      const updatedBook = res.data.find(b => b.id === selectedBook.value.id)
      if (updatedBook) selectTextbook(updatedBook)
    }
  } catch {}
}
</script>
