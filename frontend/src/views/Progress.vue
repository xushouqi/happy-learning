<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4">
    <header class="max-w-4xl mx-auto flex items-center justify-between mb-6">
      <button @click="router.back()" class="text-3xl hover:scale-110 transition-transform">←</button>
      <h1 class="text-xl font-bold text-gray-800">学习进度</h1>
      <span class="w-8"></span>
    </header>

    <div class="max-w-4xl mx-auto space-y-6">
      <!-- User selector -->
      <div class="bg-white rounded-2xl p-4 shadow-lg">
        <div class="flex gap-4 justify-center">
          <button
            v-for="user in users"
            :key="user.id"
            @click="selectUser(user.id)"
            :class="[
              'px-6 py-3 rounded-full text-lg font-bold transition-all',
              selectedUser === user.id
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
            ]"
          >
            {{ user.avatar }} {{ user.name }}
          </button>
        </div>
      </div>

      <!-- Course progress -->
      <div v-for="course in courseProgress" :key="course.id" class="bg-white rounded-2xl p-6 shadow-lg">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-gray-800">{{ course.name }}</h2>
          <span class="text-sm text-gray-500">
            {{ course.completed_units }}/{{ course.total_units }} 完成
            <span v-if="course.total_questions > 0">
              · 最高分 {{ course.best_score }}/{{ course.total_questions }}
            </span>
          </span>
        </div>

        <!-- Course progress bar -->
        <div class="w-full bg-gray-100 rounded-full h-3 mb-4">
          <div
            class="bg-secondary h-3 rounded-full transition-all duration-500"
            :style="{ width: (course.total_units ? course.completed_units / course.total_units * 100 : 0) + '%' }"
          ></div>
        </div>

        <!-- Unit list -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <div
            v-for="unit in course.units"
            :key="unit.id"
            :class="[
              'p-3 rounded-xl text-center transition-all border-2 relative group cursor-pointer',
              unit.completed
                ? 'border-green-300 bg-green-50'
                : 'border-gray-200 bg-gray-50 hover:border-primary',
            ]"
            @click="goToUnit(unit.id)"
          >
            <div class="text-sm font-semibold text-gray-700">{{ unit.order }}</div>
            <div class="text-xs text-gray-500 truncate">{{ unit.name }}</div>
            <div v-if="unit.completed" class="text-xs text-green-600 mt-1">
              {{ unit.best_score }}/{{ unit.total_questions }}
            </div>
            <!-- Type stats -->
            <div v-if="getTypeStats(unit.id)" class="mt-1 flex flex-wrap gap-0.5 justify-center">
              <span
                v-for="(stats, type) in getTypeStats(unit.id)"
                :key="type"
                class="px-1 py-0.5 rounded text-[10px]"
                :class="stats.correct >= stats.total ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'"
              >
                {{ typeShort(type) }}:{{ stats.correct }}/{{ stats.total }}
              </span>
            </div>
            <div v-if="unit.attempts > 1" class="text-xs text-gray-400">
              尝试 {{ unit.attempts }} 次
            </div>
            <div v-if="unit.last_attempt" class="text-xs text-gray-400">
              {{ formatDate(unit.last_attempt) }}
            </div>
            <!-- Clear button -->
            <button
              v-if="unit.completed || unit.attempts > 0"
              @click.stop="clearUnit(unit.id)"
              class="absolute top-1 right-1 w-5 h-5 flex items-center justify-center bg-red-100 hover:bg-red-200 text-red-500 hover:text-red-700 rounded-full text-xs font-bold transition-colors"
              title="清空学习记录"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api, { users as usersApi, scores as scoresApi } from '../api'

const router = useRouter()
const users = ref([])
const selectedUser = ref(parseInt(localStorage.getItem('userId')) || 1)
const courseProgress = ref([])
const typeStats = ref({})

const typeShortLabels = {
  image_select_word: '图词',
  image_select_sentence: '图句',
  listen_select: '听选',
  listen_select_word: '听词',
  listen_spell: '拼词',
  listen_spell_sentence: '拼句',
  image_listen_spell_sentence: '图拼',
}

const typeShort = (type) => typeShortLabels[type] || type

const getTypeStats = (unitId) => typeStats.value[unitId] || null

const selectUser = (userId) => {
  selectedUser.value = userId
  localStorage.setItem('userId', userId)
  loadProgress()
}

const goToUnit = (unitId) => {
  router.push(`/video/${unitId}`)
}

const clearUnit = async (unitId) => {
  if (!confirm('确定要清空该单元的学习记录吗？')) return
  try {
    await scoresApi.clearUnit(selectedUser.value, unitId)
    await loadProgress()
  } catch {}
}

const formatDate = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const loadProgress = async () => {
  try {
    const [progressRes, statsRes] = await Promise.all([
      api.get(`/progress/user/${selectedUser.value}/textbooks`),
      scoresApi.typeStats(selectedUser.value),
    ])
    courseProgress.value = progressRes.data
    typeStats.value = statsRes.data
  } catch {
    courseProgress.value = []
    typeStats.value = {}
  }
}

onMounted(async () => {
  try {
    const res = await usersApi.list()
    users.value = res.data
  } catch {}
  loadProgress()
})
</script>
