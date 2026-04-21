<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4">
    <header class="flex items-center justify-between mb-6">
      <button @click="router.push('/')" class="text-3xl hover:scale-110 transition-transform">🏠</button>
      <h1 class="text-2xl font-bold text-primary">{{ greeting }}</h1>
      <div class="flex gap-3">
        <button @click="router.push('/wrongbook')" class="text-3xl hover:scale-110 transition-transform relative">📝<span v-if="wrongCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">{{ wrongCount }}</span></button>
        <button @click="router.push('/calendar')" class="text-3xl hover:scale-110 transition-transform">📅</button>
        <button @click="router.push('/progress')" class="text-3xl hover:scale-110 transition-transform">📊</button>
      </div>
    </header>

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
          <button
            v-for="unit in selectedBook.units"
            :key="unit.id"
            @click="startUnit(unit)"
            class="w-full flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-accent/30 transition-all"
          >
            <span class="font-semibold text-gray-700">{{ unit.name }}</span>
            <span class="text-primary">开始 →</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { textbooks as textbooksApi, progress as progressApi, scores as scoresApi } from '../api'

const router = useRouter()
const textbookList = ref([])
const selectedBook = ref(null)
const progressData = ref([])
const userProgress = ref([])
const wrongCount = ref(0)

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
  selectedBook.value = book
}

const startUnit = (unit) => {
  router.push(`/quiz/${unit.id}`)
}
</script>
