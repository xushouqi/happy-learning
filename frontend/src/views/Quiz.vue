<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4 flex flex-col items-center">
    <header class="w-full max-w-2xl flex items-center justify-between mb-6">
      <button @click="route.name === 'quizWrong' ? router.push('/wrongbook') : router.push('/dashboard')" class="text-3xl hover:scale-110 transition-transform">←</button>
      <span class="text-sm text-gray-600">{{ route.name === 'quizWrong' ? '错题重做' : '第' }} {{ current + 1 }} / {{ questions.length }} {{ route.name === 'quizWrong' ? '题' : '题' }}</span>
      <span class="text-2xl">⭐ {{ stars }}</span>
    </header>

    <!-- Progress bar -->
    <div class="w-full max-w-2xl bg-white rounded-full h-3 mb-6">
      <div
        class="bg-secondary h-3 rounded-full transition-all duration-300"
        :style="{ width: ((current + 1) / questions.length * 100) + '%' }"
      ></div>
    </div>

    <!-- Question Card -->
    <div v-if="loadError" class="bg-white rounded-2xl p-6 shadow-lg w-full max-w-2xl text-center">
      <p class="text-2xl mb-4">😵</p>
      <p class="text-xl text-gray-700 mb-4">加载题目失败</p>
      <button @click="router.push('/dashboard')" class="px-6 py-3 bg-primary text-white rounded-full text-lg">返回首页</button>
    </div>

    <div v-else-if="currentQuestion" class="bg-white rounded-2xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-xl font-bold text-gray-800 mb-4 text-center">
        {{ questionPrompt }}
      </h2>

      <!-- Image for image_select_word -->
      <div v-if="currentQuestion.type === 'image_select_word'" class="text-center mb-4">
        <img
          :src="questionImage"
          :alt="questionPrompt"
          class="w-48 h-48 object-cover rounded-xl mx-auto border-2 border-gray-200"
          @load="imageLoaded = true"
          @error="imageLoaded = false"
        />
        <div v-if="!imageLoaded" class="w-48 h-48 flex items-center justify-center mx-auto bg-gray-100 rounded-xl border-2 border-gray-200">
          <span class="text-6xl font-bold text-gray-400">{{ currentQuestion.answer }}</span>
        </div>
        <p v-if="currentQuestion.sentence" class="text-gray-600 mt-2 text-lg italic">{{ currentQuestion.sentence }}</p>
      </div>

      <!-- listen_spell_sentence: word ordering -->
      <div v-if="currentQuestion.type === 'listen_spell_sentence'" class="text-center mb-4">
        <button @click="playAudio" class="text-4xl hover:scale-110 transition-transform mb-3">🔊</button>
        <p class="text-gray-500 mb-3">听一听，点击单词排列成正确的句子</p>
        <!-- Built sentence -->
        <div class="flex flex-wrap justify-center gap-2 mb-4 min-h-[48px] p-2 bg-gray-50 rounded-xl">
          <span
            v-for="(word, idx) in builtSentenceWords"
            :key="'built-' + idx"
            class="px-3 py-1 bg-primary text-white rounded-lg text-base font-semibold"
          >{{ word }}</span>
          <span v-if="builtSentenceWords.length === 0" class="text-gray-300 text-xl">?</span>
        </div>
        <!-- Available word tiles -->
        <div class="flex flex-wrap justify-center gap-3">
          <button
            v-for="(word, idx) in sentenceTiles"
            :key="'tile-' + idx"
            @click="addWord(word, idx)"
            :disabled="wordTileUsed[idx] || answered"
            :class="[
              'px-4 py-2 rounded-lg text-lg font-semibold transition-all border-2',
              wordTileUsed[idx]
                ? 'border-gray-100 bg-gray-100 text-gray-300 opacity-30'
                : 'border-gray-200 bg-white hover:border-primary hover:bg-pink-50',
            ]"
          >{{ word }}</button>
        </div>
        <button
          v-if="builtSentenceWords.length > 0 && !answered"
          @click="clearSentence"
          class="mt-3 px-4 py-2 bg-gray-200 text-gray-600 rounded-full text-base font-semibold hover:bg-gray-300 transition-all"
        >✕ 清除重排</button>
        <button
          v-if="builtSentenceWords.length === sentenceTiles.length && !answered"
          @click="submitSentence"
          class="mt-3 px-6 py-2 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
        >确认 ✓</button>
      </div>

      <!-- image_listen_spell_sentence: image + audio + word ordering -->
      <div v-if="currentQuestion.type === 'image_listen_spell_sentence'" class="text-center mb-4">
        <img
          v-if="currentQuestion.image_url"
          :src="'/' + currentQuestion.image_url"
          :alt="questionPrompt"
          class="w-40 h-40 object-cover rounded-xl mx-auto border-2 border-gray-200 mb-3"
          @load="imageLoaded = true"
          @error="imageLoaded = false"
        />
        <div v-if="!imageLoaded && currentQuestion.image_url" class="w-40 h-40 flex items-center justify-center mx-auto bg-gray-100 rounded-xl border-2 border-gray-200 mb-3">
          <span class="text-4xl">🖼️</span>
        </div>
        <button @click="playAudio" class="text-4xl hover:scale-110 transition-transform mb-3">🔊</button>
        <p class="text-gray-500 mb-3">看图听音，点击单词排列成正确的句子</p>
        <!-- Built sentence -->
        <div class="flex flex-wrap justify-center gap-2 mb-4 min-h-[48px] p-2 bg-gray-50 rounded-xl">
          <span
            v-for="(word, idx) in builtSentenceWords"
            :key="'built-' + idx"
            class="px-3 py-1 bg-primary text-white rounded-lg text-base font-semibold"
          >{{ word }}</span>
          <span v-if="builtSentenceWords.length === 0" class="text-gray-300 text-xl">?</span>
        </div>
        <!-- Available word tiles -->
        <div class="flex flex-wrap justify-center gap-3">
          <button
            v-for="(word, idx) in sentenceTiles"
            :key="'tile-' + idx"
            @click="addWord(word, idx)"
            :disabled="wordTileUsed[idx] || answered"
            :class="[
              'px-4 py-2 rounded-lg text-lg font-semibold transition-all border-2',
              wordTileUsed[idx]
                ? 'border-gray-100 bg-gray-100 text-gray-300 opacity-30'
                : 'border-gray-200 bg-white hover:border-primary hover:bg-pink-50',
            ]"
          >{{ word }}</button>
        </div>
        <button
          v-if="builtSentenceWords.length > 0 && !answered"
          @click="clearSentence"
          class="mt-3 px-4 py-2 bg-gray-200 text-gray-600 rounded-full text-base font-semibold hover:bg-gray-300 transition-all"
        >✕ 清除重排</button>
        <button
          v-if="builtSentenceWords.length === sentenceTiles.length && !answered"
          @click="submitSentence"
          class="mt-3 px-6 py-2 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
        >确认 ✓</button>
      </div>

      <!-- Image for image_select_sentence -->
      <div v-if="currentQuestion.type === 'image_select_sentence'" class="text-center mb-4">
        <img
          v-if="currentQuestion.image_url"
          :src="'/' + currentQuestion.image_url"
          :alt="questionPrompt"
          class="w-48 h-48 object-cover rounded-xl mx-auto border-2 border-gray-200"
          @load="imageLoaded = true"
          @error="imageLoaded = false"
        />
        <div v-if="!imageLoaded" class="w-48 h-48 flex items-center justify-center mx-auto bg-gray-100 rounded-xl border-2 border-gray-200">
          <span class="text-6xl font-bold text-gray-400" v-if="currentQuestion.image_url">{{ currentQuestion.answer }}</span>
          <span class="text-2xl" v-else>🖼️</span>
        </div>
        <p v-if="currentQuestion.audio_text" class="text-gray-500 mt-2">
          <button @click="playAudio" class="text-3xl hover:scale-110 transition-transform">🔊</button>
        </p>
      </div>

      <!-- Audio button for listen_select_word -->
      <div v-if="currentQuestion.type === 'listen_select_word'" class="text-center mb-4">
        <button @click="playAudio" class="text-5xl hover:scale-110 transition-transform">🔊</button>
      </div>

      <!-- Scramble/listen spell word UI -->
      <div v-if="currentQuestion.type === 'listen_spell'" class="text-center mb-4">
        <button @click="playAudio" class="text-4xl hover:scale-110 transition-transform mb-3">🔊</button>
        <p class="text-gray-500 mb-3">听一听，点击字母拼出正确的词</p>
        <div class="flex justify-center gap-2 mb-4 min-h-[48px]">
          <span
            v-for="(letter, idx) in builtLetters"
            :key="'built-' + idx"
            class="w-10 h-10 flex items-center justify-center bg-primary text-white rounded-lg text-lg font-bold"
          >{{ letter }}</span>
          <span v-if="builtLetters.length === 0" class="text-gray-300 text-2xl">?</span>
        </div>
        <div class="flex flex-wrap justify-center gap-3">
          <button
            v-for="(letter, idx) in scrambleTiles"
            :key="'tile-' + idx"
            @click="addLetter(letter, idx)"
            :disabled="tileUsed[idx] || answered"
            :class="[
              'w-12 h-12 rounded-lg text-xl font-bold transition-all border-2',
              tileUsed[idx]
                ? 'border-gray-100 bg-gray-100 text-gray-300 opacity-30'
                : 'border-gray-200 bg-white hover:border-primary hover:bg-pink-50',
            ]"
          >{{ letter }}</button>
        </div>
        <button
          v-if="builtLetters.length > 0 && !answered"
          @click="clearBuilt"
          class="mt-3 px-4 py-2 bg-gray-200 text-gray-600 rounded-full text-base font-semibold hover:bg-gray-300 transition-all"
        >✕ 清除重拼</button>
        <button
          v-if="builtLetters.length === scrambleTiles.length && !answered"
          @click="submitScramble"
          class="mt-3 px-6 py-2 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
        >确认 ✓</button>
      </div>

      <!-- Options (listen_select_word, image_select_word, image_select_sentence) -->
      <div v-if="['listen_select_word', 'image_select_word', 'image_select_sentence'].includes(currentQuestion.type)" class="grid grid-cols-2 gap-4">
        <button
          v-for="(option, idx) in currentQuestion.options"
          :key="option"
          @click="selectAnswer(option)"
          :disabled="answered"
          :class="[
            'p-4 rounded-xl text-lg font-semibold transition-all border-2',
            getOptionClass(option),
          ]"
        >
          {{ option }}
        </button>
      </div>

      <!-- Feedback -->
      <div v-if="feedback" class="mt-4 text-center">
        <span :class="['text-4xl', isCorrect ? 'animate-bounce' : 'animate-shake']">
          {{ isCorrect ? '✅' : '❌' }}
        </span>
        <p :class="['text-xl mt-2', isCorrect ? 'text-green-600' : 'text-red-500']">
          {{ isCorrect ? '太棒了！' : `正确答案: ${currentQuestion.answer}` }}
        </p>
      </div>
    </div>

    <!-- Next Button -->
    <button
      v-if="answered"
      @click="nextQuestion"
      class="mt-6 px-8 py-3 bg-accent text-gray-800 rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
    >
      {{ current + 1 < questions.length ? '下一题 →' : '查看成绩 🎉' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { questions as questionsApi, scores as scoresApi } from '../api'

const router = useRouter()
const route = useRoute()

const questions = ref([])
const current = ref(0)
const stars = ref(0)
const answered = ref(false)
const selectedOption = ref(null)
const isCorrect = ref(false)
const feedback = ref(false)
const results = ref([])
const imageLoaded = ref(true)
const wordToImage = ref({})

// Shuffle utility
const shuffleArray = (arr) => {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// Scramble/spell word state
const builtLetters = ref([])
const tileUsed = ref([])

// Sentence ordering state
const builtSentenceWords = ref([])
const wordTileUsed = ref([])

const scrambleTiles = computed(() => {
  const q = currentQuestion.value
  if (!q || q.type !== 'listen_spell') return []
  const word = q.answer || ''
  let letters = word.split('')
  // Shuffle until different from original
  let shuffled = shuffleArray(letters)
  let attempts = 0
  while (shuffled.join('') === word && attempts < 10) {
    shuffled = shuffleArray(letters)
    attempts++
  }
  return shuffled
})

const sentenceTiles = computed(() => {
  const q = currentQuestion.value
  if (!q || !['listen_spell_sentence', 'image_listen_spell_sentence'].includes(q.type)) return []
  const words = q.options || []
  // Shuffle until different from original order
  let shuffled = shuffleArray(words)
  let attempts = 0
  while (shuffled.join(' ') === q.answer && attempts < 10) {
    shuffled = shuffleArray(words)
    attempts++
  }
  return shuffled
})

const questionImage = computed(() => {
  const q = currentQuestion.value
  if (!q || q.type !== 'image_select_word') return ''
  let url = ''
  if (q.image_url) {
    url = q.image_url.startsWith('/') ? q.image_url : '/' + q.image_url
  } else {
    const answerKey = q.answer.toLowerCase()
    url = wordToImage.value[answerKey] || `https://image.pollinations.ai/prompt/simple+cartoon+illustration+of+${encodeURIComponent(q.answer)}+for+kids?width=300&height=300&nologo=true`
  }
  const sep = url.includes('?') ? '&' : '?'
  return `${url}${sep}v=${new Date().getTime()}`
})

const addLetter = (letter, idx) => {
  if (tileUsed.value[idx] || answered.value) return
  tileUsed.value[idx] = true
  builtLetters.value.push(letter)
}

const clearBuilt = () => {
  builtLetters.value = []
  tileUsed.value = []
}

const submitScramble = () => {
  if (answered.value) return
  answered.value = true
  const word = builtLetters.value.join('').toLowerCase()
  isCorrect.value = word === currentQuestion.value.answer.toLowerCase()
  if (isCorrect.value) stars.value++
  results.value.push({
    questionId: currentQuestion.value.id,
    correct: isCorrect.value,
    score: isCorrect.value ? 10 : 0,
  })
  feedback.value = true
  if (isCorrect.value) {
    setTimeout(() => nextQuestion(), 1000)
  }
}

const addWord = (word, idx) => {
  if (wordTileUsed.value[idx] || answered.value) return
  wordTileUsed.value[idx] = true
  builtSentenceWords.value.push(word)
}

const clearSentence = () => {
  builtSentenceWords.value = []
  wordTileUsed.value = []
}

const submitSentence = () => {
  if (answered.value) return
  answered.value = true
  const sentence = builtSentenceWords.value.join(' ')
  isCorrect.value = sentence.toLowerCase() === currentQuestion.value.answer.toLowerCase()
  if (isCorrect.value) stars.value++
  results.value.push({
    questionId: currentQuestion.value.id,
    correct: isCorrect.value,
    score: isCorrect.value ? 10 : 0,
  })
  feedback.value = true
  if (isCorrect.value) {
    setTimeout(() => nextQuestion(), 1000)
  }
}

const currentQuestion = computed(() => questions.value[current.value])

const questionPrompt = computed(() => {
  const q = currentQuestion.value
  if (!q) return ''
  switch (q.type) {
    case 'listen_select_word': return '听一听，选一选！'
    case 'image_select_word': return '看图选词！'
    case 'image_select_sentence': return '看图选句子！'
    case 'listen_spell': return '拼一拼！'
    case 'listen_spell_sentence': return '拼一拼句子！'
    case 'image_listen_spell_sentence': return '看图听音拼句！'
    default: return '选一选！'
  }
})

const loadError = ref(false)

const getUserId = () => parseInt(localStorage.getItem('userId'))

onMounted(async () => {
  try {
    const imgRes = await questionsApi.wordToImage()
    wordToImage.value = imgRes.data

    if (route.name === 'quizWrong') {
      // Wrong question review mode
      const userId = getUserId()
      if (!userId) { loadError.value = true; return }
      const res = await scoresApi.wrongQuiz(userId)
      const qids = res.data.question_ids
      if (!qids || qids.length === 0) {
        questions.value = []
        return
      }
      const qRes = await questionsApi.byIds(qids)
      questions.value = shuffleArray(qRes.data)
    } else {
      // Normal unit quiz mode
      const unitId = route.params.unitId
      const types = route.query.types
      const qRes = await questionsApi.quiz(unitId, types)
      questions.value = qRes.data
    }
  } catch {
    loadError.value = true
    questions.value = []
  }
})

const playAudio = async () => {
  if (!currentQuestion.value?.audio_text) return
  try {
    const url = `/api/tts/speak?text=${encodeURIComponent(currentQuestion.value.audio_text)}`
    const audio = new Audio(url)
    await audio.play()
  } catch {
    // Fallback to SpeechSynthesis if TTS endpoint fails
    const utterance = new SpeechSynthesisUtterance(currentQuestion.value.audio_text)
    utterance.lang = 'en-US'
    utterance.rate = 0.6
    speechSynthesis.speak(utterance)
  }
}

// Auto-play audio when question changes
watch(currentQuestion, (q) => {
  if (!q) return
  if (['listen_select_word', 'listen_spell', 'listen_spell_sentence', 'image_listen_spell_sentence'].includes(q.type)) {
    setTimeout(() => playAudio(), 300)
  }
  imageLoaded.value = true
})

const getOptionClass = (option) => {
  if (!answered.value) return 'border-gray-200 bg-gray-50 hover:border-primary hover:bg-pink-50'
  if (option === currentQuestion.value.answer) return 'border-green-400 bg-green-100'
  if (option === selectedOption.value && !isCorrect.value) return 'border-red-400 bg-red-100'
  return 'border-gray-200 bg-gray-50 opacity-50'
}

const selectAnswer = (option) => {
  if (answered.value) return
  selectedOption.value = option
  answered.value = true
  isCorrect.value = option === currentQuestion.value.answer

  if (isCorrect.value) stars.value++

  results.value.push({
    questionId: currentQuestion.value.id,
    correct: isCorrect.value,
    score: isCorrect.value ? 10 : 0,
  })

  feedback.value = true
  if (isCorrect.value) {
    setTimeout(() => nextQuestion(), 1000)
  }
}

const nextQuestion = async () => {
  const last = results.value[results.value.length - 1]
  const userId = getUserId()
  if (userId) {
    try {
      await scoresApi.record({
        user_id: userId,
        question_id: last.questionId,
        correct: last.correct,
        score: last.score,
      })
    } catch {}
  }

  if (current.value + 1 < questions.value.length) {
    current.value++
    answered.value = false
    selectedOption.value = null
    isCorrect.value = false
    feedback.value = false
    imageLoaded.value = true
    builtLetters.value = []
    tileUsed.value = []
    builtSentenceWords.value = []
    wordTileUsed.value = []
  } else {
    if (route.name !== 'quizWrong' && userId) {
      try {
        await scoresApi.recordUnitComplete({
          user_id: userId,
          unit_id: parseInt(route.params.unitId),
          score: stars.value,
          total: questions.value.length,
        })
      } catch {}
    }

    if (route.name === 'quizWrong') {
      router.push('/wrongbook')
    } else {
      router.push({
        name: 'results',
        query: {
          total: stars.value,
          count: questions.value.length,
          unitId: route.params.unitId,
        },
      })
    }
  }
}
</script>

<style>
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}
.animate-shake { animation: shake 0.4s ease; }
</style>
