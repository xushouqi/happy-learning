<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-200 via-pink-100 to-blue-200 p-4 flex flex-col items-center">
    <header class="w-full max-w-2xl flex items-center justify-between mb-6">
      <button @click="router.push('/dashboard')" class="text-3xl hover:scale-110 transition-transform">←</button>
      <span class="text-xl font-bold text-gray-700">🎤 语音发音检测原型</span>
      <span class="text-2xl">⭐ {{ totalScore }}</span>
    </header>

    <div class="bg-white rounded-2xl p-6 shadow-lg w-full max-w-2xl">
      <!-- Target sentence -->
      <div class="text-center mb-6">
        <p class="text-gray-500 mb-2">请朗读以下句子：</p>
        <div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-4">
          <p class="text-2xl font-bold text-gray-800">{{ currentSentence }}</p>
        </div>
        <button @click="playTargetAudio" class="mt-3 text-3xl hover:scale-110 transition-transform">🔊</button>
      </div>

      <!-- Recording status -->
      <div v-if="isListening" class="text-center mb-6">
        <div class="animate-pulse text-6xl mb-3">🎙️</div>
        <p class="text-xl text-red-500 font-bold">正在录音中...</p>
        <p class="text-gray-500">请大声朗读句子</p>
      </div>

      <!-- User transcript -->
      <div v-if="userTranscript" class="text-center mb-6">
        <p class="text-gray-500 mb-2">你说的是：</p>
        <div :class="['rounded-xl p-4', isCorrect ? 'bg-green-100' : 'bg-yellow-100']">
          <p class="text-2xl font-bold" :class="isCorrect ? 'text-green-600' : 'text-yellow-600'">
            {{ userTranscript }}
          </p>
        </div>
      </div>

      <!-- Score feedback -->
      <div v-if="showFeedback" class="text-center mb-6">
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

      <!-- Control buttons -->
      <div class="flex justify-center gap-4 mt-6">
        <button
          v-if="!isListening && !showFeedback"
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
          v-if="showFeedback && !isCorrect"
          @click="retry"
          class="px-6 py-3 bg-yellow-400 text-gray-800 rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
        >
          🔄 再试一次
        </button>
        <button
          v-if="showFeedback && (isCorrect || attempts >= 3)"
          @click="nextSentence"
          class="px-6 py-3 bg-accent text-gray-800 rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
        >
          {{ currentIndex < sentences.length - 1 ? '下一句 →' : '完成 🎉' }}
        </button>
      </div>

      <!-- Attempts counter -->
      <div v-if="attempts > 0" class="text-center mt-4 text-gray-500">
        已尝试 {{ attempts }} 次 (最多3次)
      </div>

      <!-- Browser support warning -->
      <div v-if="!browserSupported" class="mt-6 p-4 bg-red-100 rounded-xl text-center">
        <p class="text-red-600 font-bold">⚠️ 你的浏览器不支持语音识别</p>
        <p class="text-gray-600 text-sm mt-2">请使用 Chrome、Edge 或 Safari 浏览器</p>
      </div>
    </div>

    <!-- Sentence list -->
    <div class="mt-6 w-full max-w-2xl">
      <div class="bg-white rounded-xl p-4 shadow">
        <p class="text-gray-600 font-bold mb-3">句子列表 ({{ currentIndex + 1 }}/{{ sentences.length }})</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(s, idx) in sentences"
            :key="idx"
            :class="[
              'px-3 py-1 rounded-lg text-sm',
              idx === currentIndex ? 'bg-primary text-white' :
              completed[idx] ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
            ]"
          >
            {{ idx + 1 }} {{ completed[idx] ? '✓' : '' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { speak } from '../lib/tts'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const sentences = ref([
  "I like apples",
  "She is happy",
  "The cat is sleeping",
  "What is your name",
  "Good morning teacher"
])

const currentIndex = ref(0)
const completed = ref({})
const totalScore = ref(0)
const attempts = ref(0)
const isListening = ref(false)
const userTranscript = ref('')
const showFeedback = ref(false)
const browserSupported = ref(true)

let recognition = null

const currentSentence = computed(() => sentences.value[currentIndex.value])
const isCorrect = computed(() => {
  if (!userTranscript.value) return false
  return normalizeText(userTranscript.value) === normalizeText(currentSentence.value)
})
const similarityScore = computed(() => {
  if (!userTranscript.value) return 0
  return calculateSimilarity(userTranscript.value, currentSentence.value)
})
const earnedScore = computed(() => {
  if (isCorrect.value && attempts.value === 1) return 10
  if (isCorrect.value && attempts.value === 2) return 7
  if (isCorrect.value && attempts.value === 3) return 5
  return 0
})

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
  try {
    const url = `/api/tts/speak?text=${encodeURIComponent(currentSentence.value)}`
    const audio = new Audio(url)
    await audio.play()
  } catch {
    // Fallback to browser SpeechSynthesis
    const utterance = new SpeechSynthesisUtterance(currentSentence.value)
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
      completed.value[currentIndex.value] = true
    }
  }

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error)
    isListening.value = false
    if (event.error === 'no-speech') {
      userTranscript.value = '(未检测到语音)'
      showFeedback.value = true
    }
  }

  recognition.onend = () => {
    isListening.value = false
  }
}

const startListening = async () => {
  if (!recognition) return

  // 先请求麦克风权限
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach(track => track.stop()) // 立即释放，仅用于触发权限请求
  } catch (err) {
    console.error('Microphone permission denied:', err)
    userTranscript.value = '(麦克风权限被拒绝)'
    showFeedback.value = true
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

const nextSentence = () => {
  if (currentIndex.value < sentences.value.length - 1) {
    currentIndex.value++
    userTranscript.value = ''
    showFeedback.value = false
    attempts.value = 0
  } else {
    router.push('/dashboard')
  }
}

onMounted(() => {
  initSpeechRecognition()
})

onUnmounted(() => {
  if (recognition) {
    recognition.stop()
  }
})
</script>
