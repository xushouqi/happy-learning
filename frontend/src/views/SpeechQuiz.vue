<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-200 via-pink-100 to-blue-200 p-4 flex flex-col items-center">
    <header class="w-full max-w-2xl flex items-center justify-between mb-6">
      <button @click="router.push('/dashboard')" class="text-3xl hover:scale-110 transition-transform">←</button>
      <span class="text-xl font-bold text-gray-700">
        {{ practiceType === 'listen_read_sentence' ? '🎤 听音读句' : '🎤 看图读词' }}
      </span>
      <span class="text-2xl">⭐ {{ totalScore }}</span>
    </header>

    <!-- Progress bar -->
    <div class="w-full max-w-2xl bg-white rounded-full h-3 mb-6">
      <div
        class="bg-secondary h-3 rounded-full transition-all duration-300"
        :style="{ width: ((currentIndex + 1) / questions.length * 100) + '%' }"
      ></div>
    </div>

    <div v-if="loadError" class="bg-white rounded-2xl p-6 shadow-lg w-full max-w-2xl text-center">
      <p class="text-2xl mb-4">😵</p>
      <p class="text-xl text-gray-700 mb-4">加载题目失败</p>
      <button @click="router.push('/dashboard')" class="px-6 py-3 bg-primary text-white rounded-full text-lg">返回首页</button>
    </div>

    <div v-else-if="questions.length === 0" class="bg-white rounded-2xl p-6 shadow-lg w-full max-w-2xl text-center">
      <p class="text-2xl mb-4">📭</p>
      <p class="text-xl text-gray-700 mb-4">该单元暂无此类题目</p>
      <button @click="router.push('/dashboard')" class="px-6 py-3 bg-primary text-white rounded-full text-lg">返回首页</button>
    </div>

    <div v-else class="bg-white rounded-2xl p-6 shadow-lg w-full max-w-2xl">
      <!-- Question counter -->
      <p class="text-sm text-gray-500 mb-4 text-center">第 {{ currentIndex + 1 }} / {{ questions.length }} 题</p>

      <!-- Image for image_read_word -->
      <div v-if="currentQuestion?.type === 'image_read_word'" class="text-center mb-6">
        <p class="text-gray-500 mb-2">看图朗读单词：</p>
        <img
          :src="getImageUrl(currentQuestion?.image_url)"
          :alt="currentQuestion?.target_text"
          class="w-48 h-48 object-cover rounded-xl mx-auto border-2 border-gray-200 mb-4"
          @error="imageError = true"
        />
        <div v-if="imageError" class="w-48 h-48 flex items-center justify-center mx-auto bg-gray-100 rounded-xl border-2 border-gray-200 mb-4">
          <span class="text-6xl font-bold text-gray-400">{{ currentQuestion?.target_text }}</span>
        </div>
        <div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-4">
          <p class="text-3xl font-bold text-gray-800">{{ currentQuestion?.target_text }}</p>
        </div>
      </div>

      <!-- Audio button for listen_read_sentence -->
      <div v-if="currentQuestion?.type === 'listen_read_sentence'" class="text-center mb-6">
        <p class="text-gray-500 mb-2">听音朗读句子：</p>
        <div v-if="currentQuestion?.image_url" class="mb-4">
          <img
            :src="getImageUrl(currentQuestion?.image_url)"
            class="w-40 h-40 object-cover rounded-xl mx-auto border-2 border-gray-200"
            @error="currentQuestion.image_url = null"
          />
        </div>
        <button @click="playTargetAudio" class="text-5xl hover:scale-110 transition-transform mb-3">🔊</button>
        <p class="text-gray-400 mb-3">点击播放听句子</p>
        <div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-4">
          <p class="text-2xl font-bold text-gray-800">{{ currentQuestion?.target_text }}</p>
        </div>
      </div>

      <!-- Recording status -->
      <div v-if="isListening" class="text-center mb-6">
        <div class="animate-pulse text-6xl mb-3">🎙️</div>
        <p class="text-xl text-red-500 font-bold">正在录音中...</p>
        <p class="text-gray-500">请大声朗读</p>
      </div>

      <!-- User transcript -->
      <div v-if="userTranscript && showFeedback" class="text-center mb-4">
        <p class="text-gray-500 mb-2">你说的是：</p>
        <div :class="['rounded-xl p-4', isCorrect ? 'bg-green-100' : 'bg-yellow-100']">
          <p class="text-xl font-bold" :class="isCorrect ? 'text-green-600' : 'text-yellow-600'">
            {{ userTranscript }}
          </p>
        </div>
      </div>

      <!-- Score feedback -->
      <div v-if="showFeedback" class="text-center mb-4">
        <div class="text-6xl mb-3">{{ isCorrect ? '🎉' : '😅' }}</div>
        <p class="text-xl font-bold" :class="isCorrect ? 'text-green-600' : 'text-yellow-600'">
          {{ isCorrect ? '发音正确！' : '再试一次' }}
        </p>
        <div class="mt-3 flex justify-center gap-2">
          <span class="px-3 py-1 bg-gray-100 rounded-lg text-sm">
            相似度: {{ similarityScore }}%
          </span>
          <span class="px-3 py-1 bg-gray-100 rounded-lg text-sm">
            得分: +{{ earnedScore }}
          </span>
        </div>
      </div>

      <!-- Browser support warning -->
      <div v-if="!browserSupported" class="mb-6 p-4 bg-red-100 rounded-xl text-center">
        <p class="text-red-600 font-bold">⚠️ 你的浏览器不支持语音识别</p>
        <p class="text-gray-600 text-sm mt-2">请使用 Chrome、Edge 或 Safari 浏览器</p>
      </div>

      <!-- Control buttons -->
      <div class="flex justify-center gap-4 mt-4">
        <button
          v-if="!isListening && !showFeedback && browserSupported"
          @click="startListening"
          class="px-8 py-4 bg-primary text-white rounded-full text-xl font-bold hover:bg-opacity-80 transition-all shadow-lg"
        >
          🎤 开始录音
        </button>
        <button
          v-if="isListening"
          @click="stopListening"
          class="px-8 py-4 bg-red-500 text-white rounded-full text-xl font-bold hover:bg-opacity-80 transition-all"
        >
          ⏹️ 停止录音
        </button>
        <button
          v-if="showFeedback && !isCorrect && attempts < 3"
          @click="retry"
          class="px-6 py-3 bg-yellow-400 text-gray-800 rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
        >
          🔄 再试一次
        </button>
        <button
          v-if="showFeedback && (isCorrect || attempts >= 3)"
          @click="nextQuestion"
          class="px-6 py-3 bg-accent text-gray-800 rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
        >
          {{ currentIndex < questions.length - 1 ? '下一题 →' : '完成 🎉' }}
        </button>
      </div>

      <!-- Attempts counter -->
      <div v-if="attempts > 0" class="text-center mt-4 text-gray-500">
        已尝试 {{ attempts }} 次 (最多3次)
      </div>
    </div>
  </div>
</template>

<script setup>
import { speak } from '../lib/tts'
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const questions = ref([])
const currentIndex = ref(0)
const totalScore = ref(0)
const attempts = ref(0)
const isListening = ref(false)
const userTranscript = ref('')
const showFeedback = ref(false)
const browserSupported = ref(true)
const loadError = ref(false)
const imageError = ref(false)

let recognition = null

const practiceType = computed(() => route.query.type || 'listen_read_sentence')
const unitId = computed(() => route.params.unitId)

const currentQuestion = computed(() => questions.value[currentIndex.value])

const isCorrect = computed(() => {
  if (!userTranscript.value || !currentQuestion.value) return false
  return normalizeText(userTranscript.value) === normalizeText(currentQuestion.value.target_text)
})

const similarityScore = computed(() => {
  if (!userTranscript.value || !currentQuestion.value) return 0
  return calculateSimilarity(userTranscript.value, currentQuestion.value.target_text)
})

const earnedScore = computed(() => {
  if (isCorrect.value && attempts.value === 1) return 10
  if (isCorrect.value && attempts.value === 2) return 7
  if (isCorrect.value && attempts.value === 3) return 5
  return 0
})

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return '/' + path
}

const normalizeText = (text) => {
  return text.toLowerCase().replace(/[^\w\s]/g, '').trim()
}

const calculateSimilarity = (text1, text2) => {
  const s1 = normalizeText(text1)
  const s2 = normalizeText(text2)
  if (s1 === s2) return 100

  const words1 = s1.split(' ')
  const words2 = s2.split(' ')
  const common = words1.filter(w => words2.includes(w)).length
  const maxLen = Math.max(words1.length, words2.length)
  return Math.round((common / maxLen) * 100)
}

const playTargetAudio = async () => {
  if (!currentQuestion.value?.audio_text) return
  try {
    const url = `/api/tts/speak?text=${encodeURIComponent(currentQuestion.value.audio_text)}`
    const audio = new Audio(url)
    await audio.play()
  } catch {
    const utterance = new SpeechSynthesisUtterance(currentQuestion.value.audio_text)
    utterance.lang = 'en-US'
    utterance.rate = 0.8
    speechSynthesis.speak(utterance)
  }
}

const initSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    browserSupported.value = false
    return
  }

  recognition = new SpeechRecognition()
  recognition.lang = 'en-US'
  recognition.continuous = false
  recognition.interimResults = false
  recognition.maxAlternatives = 1

  recognition.onstart = () => {
    isListening.value = true
  }

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    userTranscript.value = transcript
    isListening.value = false
    showFeedback.value = true

    if (isCorrect.value) {
      totalScore.value += earnedScore.value
    }
  }

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error)
    isListening.value = false
    if (event.error === 'no-speech') {
      userTranscript.value = '(未检测到语音)'
      showFeedback.value = true
    } else if (event.error === 'not-allowed') {
      browserSupported.value = false
    }
  }

  recognition.onend = () => {
    isListening.value = false
  }
}

const startListening = async () => {
  if (!recognition) return

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach(track => track.stop())
  } catch {
    userTranscript.value = '(麦克风权限被拒绝)'
    showFeedback.value = true
    browserSupported.value = false
    return
  }

  userTranscript.value = ''
  showFeedback.value = false
  attempts.value++
  recognition.start()
}

const stopListening = () => {
  if (!recognition) return
  recognition.stop()
}

const retry = () => {
  userTranscript.value = ''
  showFeedback.value = false
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
    userTranscript.value = ''
    showFeedback.value = false
    attempts.value = 0
    imageError.value = false
  } else {
    router.push({
      path: '/results',
      query: {
        total: totalScore.value,
        count: questions.value.length,
        unitId: unitId.value,
      }
    })
  }
}

// Auto-play audio for listen_read_sentence
watch(currentQuestion, (q) => {
  if (!q) return
  imageError.value = false
  if (q.type === 'listen_read_sentence' && q.audio_text) {
    setTimeout(() => playTargetAudio(), 500)
  }
})

onMounted(async () => {
  initSpeechRecognition()
  try {
    const res = await axios.get(`/api/questions/speech-practice/${unitId.value}`, {
      params: { practice_type: practiceType.value }
    })
    questions.value = res.data
  } catch {
    loadError.value = true
  }
})

onUnmounted(() => {
  if (recognition) {
    recognition.stop()
  }
})
</script>
