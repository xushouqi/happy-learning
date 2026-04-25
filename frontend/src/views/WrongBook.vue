<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4">
    <header class="max-w-4xl mx-auto flex items-center justify-between mb-6">
      <button @click="router.push('/dashboard')" class="text-3xl hover:scale-110 transition-transform">🏠</button>
      <h1 class="text-xl font-bold text-gray-800">错题本</h1>
      <button
        v-if="wrongQuestions.length > 0"
        @click="startReview"
        class="px-4 py-2 bg-primary text-white rounded-full text-sm font-bold hover:bg-opacity-80 transition-all"
      >
        开始重做 →
      </button>
      <span v-else class="w-16"></span>
    </header>

    <div class="max-w-4xl mx-auto">
      <!-- Empty state -->
      <div v-if="wrongQuestions.length === 0" class="bg-white rounded-2xl p-8 shadow-lg text-center">
        <p class="text-5xl mb-4">🎉</p>
        <p class="text-xl text-gray-700 font-bold">太棒了！</p>
        <p class="text-gray-500 mt-2">目前没有错题，继续保持哦！</p>
      </div>

      <!-- Stats summary -->
      <div v-else class="bg-white rounded-2xl p-4 shadow-lg mb-6">
        <p class="text-center text-gray-600 mb-3">
          共 <span class="text-primary font-bold text-lg">{{ wrongQuestions.length }}</span> 道错题
        </p>
        <!-- Type stats -->
        <div class="flex flex-wrap justify-center gap-2">
          <span
            v-for="(count, type) in typeStats"
            :key="type"
            class="px-3 py-1 rounded-full bg-red-100 text-red-600 text-sm font-semibold"
          >
            {{ typeLabel(type) }}: {{ count }}
          </span>
        </div>
      </div>

      <!-- Wrong questions list, grouped by textbook -->
      <div v-for="(group, tbId) in groupedQuestions" :key="tbId" class="bg-white rounded-2xl p-5 shadow-lg mb-6">
        <h2 class="text-lg font-bold text-gray-800 mb-4">
          {{ textbookIcon(tbId) }} {{ group.textbookName }}
          <span class="text-sm text-gray-400 font-normal">({{ group.questions.length }} 题)</span>
        </h2>
        <div class="space-y-3">
          <div
            v-for="q in group.questions"
            :key="q.id"
            class="border-2 border-gray-100 rounded-xl p-3 hover:border-accent/50 transition-all cursor-pointer"
            @click="toggleDetail(q.id)"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600 font-semibold">
                  {{ typeLabel(q.type) }}
                </span>
                <span class="text-sm text-gray-600">{{ q.unitName }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-xs text-gray-400">错 {{ q.wrongCount }} 次</span>
                <span class="text-gray-400">{{ expanded[q.id] ? '▲' : '▼' }}</span>
              </div>
            </div>
            <!-- Expanded detail -->
            <div v-if="expanded[q.id]" class="mt-3 pt-3 border-t border-gray-100 space-y-2">
              <div v-if="q.type === 'image_select_word' || q.type === 'image_select_sentence'" class="flex items-center gap-3">
                <span class="text-gray-500">题干:</span>
                <span class="text-gray-700">{{ q.sentence || '看图' }}</span>
              </div>
              <div v-if="q.type === 'listen_select' || q.type === 'listen_spell' || q.type === 'listen_spell_sentence'" class="flex items-center gap-3">
                <button @click.stop="playAudio(q.audio_text)" class="text-2xl hover:scale-110 transition-transform">🔊</button>
                <span class="text-gray-500">听音频答题</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-gray-500">正确答案:</span>
                <span class="font-bold text-green-600">{{ q.answer }}</span>
              </div>
              <div v-if="q.options && q.options.length" class="flex items-start gap-3">
                <span class="text-gray-500">选项:</span>
                <div class="flex flex-wrap gap-2">
                  <span v-for="opt in q.options" :key="opt" class="px-2 py-0.5 bg-gray-100 rounded text-sm">
                    {{ opt }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { scores } from '../api'

const router = useRouter()
const wrongQuestions = ref([])
const expanded = ref({})

const userId = computed(() => parseInt(localStorage.getItem('userId')) || 1)

const textbookIcons = {
  2: '🔤',
  3: '🐻',
  4: '🦌',
  5: '📘',
}

const typeLabels = {
  image_select_word: '看图选词',
  image_select_sentence: '看图选句',
  listen_select: '听音选词',
  listen_spell: '听音拼词',
  listen_spell_sentence: '听音拼句',
  image_listen_spell_sentence: '看图听音拼句',
}

const textbookIcon = (tbId) => textbookIcons[tbId] || '📚'
const typeLabel = (type) => typeLabels[type] || type

const typeStats = computed(() => {
  const stats = {}
  for (const q of wrongQuestions.value) {
    stats[q.type] = (stats[q.type] || 0) + 1
  }
  return stats
})

const groupedQuestions = computed(() => {
  const groups = {}
  for (const q of wrongQuestions.value) {
    if (!groups[q.textbook_id]) {
      groups[q.textbook_id] = { textbookName: q.textbook_name, questions: [] }
    }
    groups[q.textbook_id].questions.push({ ...q, unitName: q.unit_name })
  }
  return groups
})

const toggleDetail = (qid) => {
  expanded.value[qid] = !expanded.value[qid]
}

const playAudio = (text) => {
  if (!text) return
  try {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = 0.6
    speechSynthesis.speak(utterance)
  } catch {}
}

const startReview = () => {
  router.push('/quiz/wrong')
}

onMounted(async () => {
  if (!userId.value) return
  try {
    const res = await scores.wrongQuestions(userId.value)
    wrongQuestions.value = res.data
  } catch {
    wrongQuestions.value = []
  }
})
</script>
