<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4">
    <header class="max-w-4xl mx-auto flex items-center justify-between mb-6">
      <button @click="router.back()" class="text-3xl hover:scale-110 transition-transform">←</button>
      <h1 class="text-xl font-bold text-gray-800">学习日历</h1>
      <div class="flex items-center gap-3">
        <button @click="prevMonth" class="text-2xl hover:scale-110 transition-transform">◀</button>
        <span class="text-lg font-bold text-gray-700">{{ currentYear }}年{{ currentMonth }}月</span>
        <button @click="nextMonth" class="text-2xl hover:scale-110 transition-transform">▶</button>
      </div>
    </header>

    <div class="max-w-4xl mx-auto">
      <!-- Day of week headers -->
      <div class="grid grid-cols-7 gap-1 mb-2">
        <div v-for="day in weekdayNames" :key="day" class="text-center text-sm font-bold text-gray-500 py-2">
          {{ day }}
        </div>
      </div>

      <!-- Calendar grid -->
      <div class="grid grid-cols-7 gap-1">
        <!-- Empty cells before the 1st -->
        <div v-for="n in leadingEmptyDays" :key="'e-' + n" class="aspect-square rounded-xl"></div>

        <!-- Day cells -->
        <div
          v-for="day in daysInMonth"
          :key="day"
          @click="selectDay(day)"
          :class="[
            'aspect-square rounded-xl p-1 border-2 cursor-pointer transition-all flex flex-col items-center justify-start overflow-hidden text-xs',
            hasActivity(day)
              ? 'border-accent bg-accent/15 hover:bg-accent/30'
              : 'border-gray-200 bg-white/60 hover:border-primary',
            isToday(day) ? 'ring-2 ring-primary' : '',
          ]"
        >
          <span class="font-semibold leading-tight">{{ day }}</span>
          <!-- Textbook icons + counts -->
          <div class="flex flex-wrap gap-x-1 gap-y-0 mt-0.5 justify-center">
            <span
              v-for="tb in textbookSummary(day)"
              :key="tb.id"
              class="whitespace-nowrap"
            >
              {{ tb.icon }}{{ tb.count }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Day detail modal -->
    <div v-if="selectedDay !== null" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="selectedDay = null">
      <div class="bg-white rounded-2xl p-6 m-4 max-w-sm w-full max-h-[70vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold">{{ currentYear }}年{{ currentMonth }}月{{ selectedDay }}日</h2>
          <button @click="selectedDay = null" class="text-2xl">✕</button>
        </div>
        <div v-if="getEntries(selectedDay).length === 0" class="text-gray-400 text-center py-4">
          当日无学习记录
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(entry, idx) in getEntries(selectedDay)"
            :key="idx"
            class="p-3 rounded-xl border-2"
            :class="entry.completed ? 'border-green-300 bg-green-50' : 'border-gray-200'"
          >
            <div class="text-sm text-gray-500">{{ textbookIcon(entry.textbook_id) }} {{ entry.textbook_name }}</div>
            <div class="font-semibold text-gray-700">{{ entry.unit_name }}</div>
            <div class="text-sm mt-1">
              <span v-if="entry.total > 0">
                正确率: <span class="font-bold text-primary">{{ entry.correct }}/{{ entry.total }}</span>
                <span class="ml-1 text-xs text-gray-500">({{ Math.round(entry.correct / entry.total * 100) }}%)</span>
              </span>
              <span v-if="entry.completed" class="ml-2 text-green-600 text-xs">已完成</span>
            </div>
            <!-- Type breakdown -->
            <div v-if="entry.type_stats && Object.keys(entry.type_stats).length > 0" class="mt-2 flex flex-wrap gap-1">
              <span
                v-for="(stats, type) in entry.type_stats"
                :key="type"
                class="px-2 py-0.5 rounded text-xs"
                :class="stats.correct >= stats.total ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'"
              >
                {{ typeLabel(type) }}: {{ stats.correct }}/{{ stats.total }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { progress } from '../api'

const router = useRouter()

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)
const calendarData = ref({})
const selectedDay = ref(null)

const textbookIcons = {
  2: '🔤',
  3: '🐻',
  4: '🦌',
  5: '📘',
  6: '🐻',
}

const typeLabels = {
  image_select_word: '看图选词',
  image_select_sentence: '看图选句',
  listen_select: '听音选词',
  listen_spell: '听音拼词',
  listen_spell_sentence: '听音拼句',
  image_listen_spell_sentence: '看图听音拼句',
}

const weekdayNames = ['日', '一', '二', '三', '四', '五', '六']

const leadingEmptyDays = computed(() => {
  const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1).getDay()
  return firstDay
})

const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 0).getDate()
})

const userId = computed(() => parseInt(localStorage.getItem('userId')) || 1)

const dateKey = (day) => {
  const y = currentYear.value
  const m = String(currentMonth.value).padStart(2, '0')
  const d = String(day).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const hasActivity = (day) => {
  const key = dateKey(day)
  return calendarData.value[key] && calendarData.value[key].length > 0
}

const getEntries = (day) => {
  const key = dateKey(day)
  return calendarData.value[key] || []
}

const isToday = (day) => {
  return day === now.getDate() && currentMonth.value === now.getMonth() + 1 && currentYear.value === now.getFullYear()
}

const textbookIcon = (tbId) => {
  return textbookIcons[tbId] || '📚'
}

const typeLabel = (type) => typeLabels[type] || type

const textbookSummary = (day) => {
  const entries = getEntries(day)
  if (entries.length === 0) return []
  const countMap = {}
  for (const e of entries) {
    countMap[e.textbook_id] = (countMap[e.textbook_id] || 0) + 1
  }
  return Object.entries(countMap).map(([id, count]) => ({
    id: parseInt(id),
    icon: textbookIcon(parseInt(id)),
    count,
  }))
}

const loadCalendar = async () => {
  if (!userId.value) return
  try {
    const res = await progress.calendar(userId.value, currentYear.value, currentMonth.value)
    calendarData.value = res.data
  } catch {
    calendarData.value = {}
  }
}

const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentYear.value--
    currentMonth.value = 12
  } else {
    currentMonth.value--
  }
  selectedDay.value = null
}

const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentYear.value++
    currentMonth.value = 1
  } else {
    currentMonth.value++
  }
  selectedDay.value = null
}

const selectDay = (day) => {
  selectedDay.value = day
}

watch([currentYear, currentMonth], loadCalendar)

onMounted(loadCalendar)
</script>
