<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4 flex flex-col items-center">
    <header class="w-full max-w-2xl flex items-center justify-between mb-6">
      <button @click="router.push('/dashboard')" class="text-3xl hover:scale-110 transition-transform">←</button>
      <h1 class="text-xl font-bold text-primary">{{ unitName }}</h1>
      <span class="text-sm text-gray-600">选择题型</span>
    </header>

    <div class="bg-white rounded-2xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-lg font-bold text-gray-800 mb-4 text-center">选择你要练习的题型</h2>

      <div class="grid grid-cols-2 gap-4 mb-6">
        <button
          v-for="type in questionTypes"
          :key="type.value"
          @click="toggleType(type.value)"
          :class="[
            'p-4 rounded-xl text-center transition-all border-2',
            selectedTypes.includes(type.value)
              ? 'border-primary bg-pink-50 shadow-md'
              : 'border-gray-200 bg-gray-50 hover:border-primary hover:bg-pink-50',
          ]"
        >
          <span class="text-3xl mb-2 block">{{ type.icon }}</span>
          <span class="font-semibold text-gray-800">{{ type.label }}</span>
          <span class="text-xs text-gray-500 mt-1 block">{{ type.desc }}</span>
          <span v-if="type.value !== 'mixed' && !availableTypes.includes(type.value)" class="text-xs text-red-500 mt-1 block">暂无题目</span>
        </button>
      </div>

      <div class="text-center text-gray-500 text-sm mb-4">
        已选择 {{ selectedTypes.length }} 种题型
      </div>

      <button
        @click="startQuiz"
        :disabled="selectedTypes.length === 0"
        :class="[
          'w-full py-3 rounded-full text-lg font-bold transition-all',
          selectedTypes.length > 0
            ? 'bg-primary text-white hover:bg-opacity-80'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed',
        ]"
      >
        开始练习 →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { questions as questionsApi, textbooks as textbooksApi } from '../api'

const router = useRouter()
const route = useRoute()

const unitName = ref('')
const availableTypes = ref([])
const selectedTypes = ref([])

const questionTypes = [
  { value: 'image_select_word', label: '看图选词', icon: '🖼️', desc: '看图片，选择正确的单词' },
  { value: 'image_select_sentence', label: '看图选句', icon: '🖼️📝', desc: '看图片，选择正确的句子' },
  { value: 'listen_select', label: '听音选词', icon: '🔊', desc: '听声音，选择正确的单词' },
  { value: 'listen_spell_sentence', label: '听音拼句', icon: '🔊🧩', desc: '听声音，拼出正确的句子' },
  { value: 'image_listen_spell_sentence', label: '看图听音拼句', icon: '🖼️🔊🧩', desc: '看图听音，拼出正确句子' },
  { value: 'listen_read_sentence', label: '听音读句', icon: '🔊🎤', desc: '听声音，朗读句子', isSpeech: true },
  { value: 'image_read_word', label: '看图读词', icon: '🖼️🎤', desc: '看图片，朗读单词', isSpeech: true },
  { value: 'mixed', label: '综合题', icon: '🎯', desc: '混合所有题型随机练习' },
]

const toggleType = (type) => {
  if (type === 'mixed') {
    if (availableTypes.value.length === 0) return
    selectedTypes.value = ['mixed']
    return
  }
  if (selectedTypes.value.includes('mixed')) {
    selectedTypes.value = []
  }
  // For speech types, always allow selection (check availability separately)
  const typeInfo = questionTypes.find(t => t.value === type)
  if (!typeInfo?.isSpeech && !availableTypes.value.includes(type)) return
  const idx = selectedTypes.value.indexOf(type)
  if (idx > -1) {
    selectedTypes.value.splice(idx, 1)
  } else {
    selectedTypes.value.push(type)
  }
}

const startQuiz = () => {
  if (selectedTypes.value.length === 0) return

  // Check if only speech types are selected
  const speechTypes = selectedTypes.value.filter(t => {
    const typeInfo = questionTypes.find(qt => qt.value === t)
    return typeInfo?.isSpeech
  })

  if (speechTypes.length === 1) {
    // Single speech type - go to speech quiz
    router.push({
      path: `/speech-quiz/${route.params.unitId}`,
      query: { type: speechTypes[0] },
    })
  } else if (speechTypes.length > 1) {
    // Multiple speech types - error, only one at a time
    alert('发音练习只能选择一种题型')
    return
  } else {
    // Regular quiz
    const types = selectedTypes.value.includes('mixed') ? null : selectedTypes.value.join(',')
    router.push({
      path: `/quiz/${route.params.unitId}`,
      query: types ? { types } : {},
    })
  }
}

onMounted(async () => {
  try {
    const [typesRes, textbooksRes] = await Promise.all([
      questionsApi.types(route.params.unitId),
      textbooksApi.list(),
    ])
    availableTypes.value = typesRes.data.types || []
    // Add speech types availability based on source types
    if (availableTypes.value.includes('image_listen_spell_sentence') || availableTypes.value.includes('listen_spell_sentence')) {
      availableTypes.value.push('listen_read_sentence')
    }
    if (availableTypes.value.includes('image_select_word')) {
      availableTypes.value.push('image_read_word')
    }
    selectedTypes.value = []

    const unitId = parseInt(route.params.unitId)
    for (const book of textbooksRes.data) {
      const unit = book.units?.find(u => u.id === unitId)
      if (unit) {
        unitName.value = unit.name
        break
      }
    }
  } catch {
    availableTypes.value = []
  }
})
</script>