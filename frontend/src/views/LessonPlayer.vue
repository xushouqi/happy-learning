<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4 flex flex-col items-center">
    <header class="w-full max-w-2xl flex items-center justify-between mb-4">
      <button @click="goBack" class="text-3xl hover:scale-110 transition-transform">←</button>
      <h1 class="text-lg font-bold text-primary text-center px-2">{{ lessonTitle }}</h1>
      <span class="text-2xl whitespace-nowrap">⭐ {{ stars }}</span>
    </header>

    <!-- 步骤进度点 -->
    <div v-if="steps.length" class="flex gap-2 mb-4">
      <span
        v-for="(s, i) in steps"
        :key="'dot-' + i"
        :class="[
          'w-3 h-3 rounded-full transition-all',
          i < stepIndex ? 'bg-secondary' : i === stepIndex ? 'bg-primary scale-125' : 'bg-gray-300',
        ]"
      ></span>
    </div>

    <!-- 加载中 / 错误 -->
    <div v-if="loading" class="bg-white rounded-2xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-3xl mb-3 animate-bounce">🎒</p>
      <p class="text-xl text-gray-600">正在准备课程…</p>
    </div>
    <div v-else-if="loadError" class="bg-white rounded-2xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-3xl mb-3">😵</p>
      <p class="text-xl text-gray-600 mb-4">课程加载失败</p>
      <button @click="goBack" class="px-6 py-3 bg-primary text-white rounded-full text-lg">返回</button>
    </div>

    <!-- ============ 故事开场 ============ -->
    <div v-else-if="currentStep.type === 'story'" class="bg-white rounded-3xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-7xl mb-5 animate-bounce">{{ currentStep.emoji }}</p>
      <h2 class="text-2xl font-bold text-gray-800 mb-4">{{ currentStep.title }}</h2>
      <p class="text-xl text-gray-600 leading-relaxed whitespace-pre-line mb-8">{{ currentStep.text }}</p>
      <button @click="nextStep" class="px-8 py-4 bg-primary text-white rounded-full text-xl font-bold hover:bg-opacity-80 transition-all animate-pulse">
        开始学习 →
      </button>
    </div>

    <!-- ============ 学一学:词卡 ============ -->
    <div v-else-if="currentStep.type === 'learn'" class="bg-white rounded-3xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-800 text-center mb-1">{{ currentStep.title }}</h2>
      <p class="text-gray-500 text-center text-sm mb-5">点一点卡片,听一听单词 🎵</p>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <button
          v-for="card in currentStep.cards"
          :key="card.word"
          @click="tapCard(card)"
          class="bg-gradient-to-b from-amber-50 to-orange-50 border-2 border-amber-200 rounded-2xl p-3 flex flex-col items-center hover:scale-105 active:scale-95 transition-transform"
        >
          <img
            v-if="card.image"
            :src="card.image"
            :alt="card.word"
            class="w-28 h-28 object-cover rounded-xl mb-2"
            @error="imgError($event, card)"
          />
          <span v-else class="w-28 h-28 flex items-center justify-center text-5xl rounded-xl mb-2 bg-gray-100">🖼️</span>
          <span class="text-xl font-bold text-gray-800">{{ card.word }}</span>
          <span class="text-sm text-amber-600 mt-0.5">{{ card.cn }}</span>
          <span v-if="card.examples" class="text-xs text-gray-500 mt-1 line-clamp-2">{{ card.examples }}</span>
          <span v-else-if="card.sentence" class="text-xs text-gray-400 mt-1 line-clamp-2">{{ card.sentence }}</span>
        </button>
      </div>
      <div class="text-center mt-6">
        <button @click="nextStep" class="px-8 py-3 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all">
          学会啦,继续 →
        </button>
      </div>
    </div>

    <!-- ============ 看动画学一学:视频点播 ============ -->
    <div v-else-if="currentStep.type === 'video'" class="bg-white rounded-3xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-800 text-center mb-1">{{ currentStep.title }}</h2>
      <p class="text-gray-500 text-center text-sm mb-5">点字母看动画,听一听这个字母的发音 🎬</p>
      <div class="space-y-3">
        <div
          v-for="(v, idx) in currentStep.videos"
          :key="v.label"
          class="border-2 border-gray-200 rounded-2xl overflow-hidden"
        >
          <button
            @click="activeVideo = idx"
            :class="[
              'w-full flex items-center justify-between px-4 py-3 text-lg font-bold transition-all',
              activeVideo === idx ? 'bg-primary text-white' : 'bg-gray-50 text-gray-700 hover:bg-pink-50',
            ]"
          >
            <span>🔤 字母 {{ v.label }}</span>
            <span>{{ activeVideo === idx ? '⏹' : '▶' }}</span>
          </button>
          <video
            v-if="activeVideo === idx"
            :key="v.url"
            class="w-full"
            controls
            autoplay
            :src="v.url"
          >你的浏览器不支持视频播放</video>
        </div>
      </div>
      <div class="text-center mt-6">
        <button @click="nextStep" class="px-8 py-3 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all">
          看完啦,继续 →
        </button>
      </div>
    </div>

    <!-- ============ 听一听,选字母 ============ -->
    <div v-else-if="currentStep.type === 'listen_letter'" class="bg-white rounded-3xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-800 text-center mb-1">{{ currentStep.title }}</h2>
      <p class="text-gray-500 text-center text-sm mb-4">第 {{ listenIndex + 1 }} / {{ currentStep.questions.length }} 题</p>
      <div class="text-center mb-5">
        <button @click="playCurrent" class="text-6xl hover:scale-110 active:scale-95 transition-transform" aria-label="播放发音">🔊</button>
        <p class="text-sm text-gray-400 mt-1">听单词,选出开头的字母</p>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <button
          v-for="(opt, idx) in currentQuestion.options"
          :key="idx"
          @click="answerLetter(opt)"
          :disabled="listenAnswered"
          :class="[
            'p-6 rounded-2xl text-4xl font-bold border-2 transition-all',
            letterOptionClass(opt),
          ]"
        >
          {{ opt }}
        </button>
      </div>
      <div v-if="listenFeedback === 'right'" class="mt-4 text-center text-2xl animate-bounce">✅ 太棒了!</div>
      <div v-else-if="listenFeedback === 'wrong'" class="mt-4 text-center text-2xl text-red-500 animate-shake">❌ 再试一次!</div>
      <div class="text-center mt-4">
        <button v-if="listenDone" @click="nextStep" class="px-8 py-3 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all">
          下一关 →
        </button>
      </div>
    </div>

    <!-- ============ 拼一拼:听音拼词 ============ -->
    <div v-else-if="currentStep.type === 'spell'" class="bg-white rounded-3xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-800 text-center mb-1">{{ currentStep.title }}</h2>
      <p class="text-gray-500 text-center text-sm mb-4">第 {{ spellIndex + 1 }} / {{ currentStep.questions.length }} 题</p>
      <div class="text-center mb-4">
        <button @click="speak(currentSpell.audio)" class="text-5xl hover:scale-110 active:scale-95 transition-transform" aria-label="播放发音">🔊</button>
        <p class="text-sm text-gray-400 mt-1">听发音,点字母拼出单词</p>
      </div>
      <!-- 已拼字母 -->
      <div class="flex flex-wrap justify-center gap-2 mb-4 min-h-[52px] p-2 bg-gray-50 rounded-xl">
        <span
          v-for="(ch, idx) in spellBuilt"
          :key="'built-' + idx"
          class="w-11 h-11 flex items-center justify-center bg-primary text-white rounded-lg text-2xl font-bold"
        >{{ ch }}</span>
        <span v-if="spellBuilt.length === 0" class="text-gray-300 text-2xl">?</span>
      </div>
      <!-- 字母 tile -->
      <div class="flex flex-wrap justify-center gap-3">
        <button
          v-for="(ch, idx) in spellTiles"
          :key="'tile-' + idx"
          @click="addSpellLetter(ch, idx)"
          :disabled="spellTileUsed[idx] || spellAnswered"
          :class="[
            'w-12 h-12 rounded-lg text-2xl font-bold transition-all border-2',
            spellTileUsed[idx]
              ? 'border-gray-100 bg-gray-100 text-gray-300 opacity-30'
              : 'border-gray-200 bg-white hover:border-primary hover:bg-pink-50 active:scale-95',
          ]"
        >{{ ch }}</button>
      </div>
      <div class="text-center mt-4">
        <button
          v-if="spellBuilt.length > 0 && !spellAnswered"
          @click="clearSpell"
          class="px-4 py-2 bg-gray-200 text-gray-600 rounded-full text-base font-semibold hover:bg-gray-300 transition-all mr-2"
        >✕ 清除</button>
        <button
          v-if="spellBuilt.length === spellTiles.length && !spellAnswered"
          @click="submitSpell"
          class="px-6 py-2 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all"
        >确认 ✓</button>
      </div>
      <div v-if="spellFeedback === 'right'" class="mt-4 text-center text-2xl animate-bounce">✅ 太棒了!</div>
      <div v-else-if="spellFeedback === 'wrong'" class="mt-4 text-center text-2xl text-red-500 animate-shake">❌ 再试一次!</div>
      <div class="text-center mt-4">
        <button v-if="spellDone" @click="nextStep" class="px-8 py-3 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all">
          下一关 →
        </button>
      </div>
    </div>

    <!-- ============ 听音选图 ============ -->
    <div v-else-if="currentStep.type === 'listen_tap'" class="bg-white rounded-3xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-800 text-center mb-1">{{ currentStep.title }}</h2>
      <p class="text-gray-500 text-center text-sm mb-4">第 {{ listenIndex + 1 }} / {{ currentStep.questions.length }} 题</p>
      <div class="text-center mb-5">
        <button @click="playCurrent" class="text-6xl hover:scale-110 active:scale-95 transition-transform" aria-label="播放发音">🔊</button>
        <p class="text-sm text-gray-400 mt-1">点喇叭听发音,再点正确的图片</p>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <button
          v-for="(opt, idx) in currentQuestion.options"
          :key="idx"
          @click="answerListen(opt.word)"
          :disabled="listenAnswered"
          :class="['rounded-2xl p-3 border-2 transition-all', optionClass(opt.word)]"
        >
          <img
            v-if="opt.image"
            :src="opt.image"
            :alt="opt.word"
            class="w-full h-32 object-cover rounded-xl mb-1"
            @error="imgError($event, opt)"
          />
          <span v-else class="w-full h-32 flex items-center justify-center text-5xl rounded-xl mb-1 bg-gray-100">🖼️</span>
          <span class="text-lg font-semibold text-gray-700">{{ opt.word }}</span>
        </button>
      </div>
      <div v-if="listenFeedback === 'right'" class="mt-4 text-center text-2xl animate-bounce">✅ 太棒了!</div>
      <div v-else-if="listenFeedback === 'wrong'" class="mt-4 text-center text-2xl text-red-500 animate-shake">❌ 再试一次!</div>
      <div class="text-center mt-4">
        <button v-if="listenDone" @click="nextStep" class="px-8 py-3 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all">
          下一关 →
        </button>
      </div>
    </div>

    <!-- ============ 看图选词 ============ -->
    <div v-else-if="currentStep.type === 'look_choose'" class="bg-white rounded-3xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-800 text-center mb-1">{{ currentStep.title }}</h2>
      <p class="text-gray-500 text-center text-sm mb-4">第 {{ lookIndex + 1 }} / {{ currentStep.questions.length }} 题</p>
      <div class="text-center mb-5">
        <img
          v-if="currentLook.image"
          :src="currentLook.image"
          :alt="currentLook.word"
          class="w-44 h-44 object-cover rounded-2xl mx-auto border-4 border-amber-200"
          @error="imgError($event, currentLook)"
        />
        <div v-else class="w-44 h-44 flex items-center justify-center text-6xl rounded-2xl mx-auto border-4 border-amber-200 bg-gray-100">🖼️</div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="(opt, idx) in currentLook.options"
          :key="idx"
          @click="answerLook(opt)"
          :disabled="lookAnswered"
          :class="['p-4 rounded-2xl text-xl font-bold border-2 transition-all', wordClass(opt)]"
        >
          {{ opt }}
        </button>
      </div>
      <div v-if="lookFeedback === 'right'" class="mt-4 text-center text-2xl animate-bounce">✅ 太棒了!</div>
      <div v-else-if="lookFeedback === 'wrong'" class="mt-4 text-center text-2xl text-red-500 animate-shake">❌ 再试一次!</div>
      <div class="text-center mt-4">
        <button v-if="lookDone" @click="nextStep" class="px-8 py-3 bg-primary text-white rounded-full text-lg font-bold hover:bg-opacity-80 transition-all">
          下一关 →
        </button>
      </div>
    </div>

    <!-- ============ 句子跟读 ============ -->
    <div v-else-if="currentStep.type === 'sentence'" class="bg-white rounded-3xl p-6 shadow-lg w-full max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-800 text-center mb-1">{{ currentStep.title }}</h2>
      <p class="text-gray-500 text-center text-sm mb-5">第 {{ sentenceIndex + 1 }} / {{ currentStep.sentences.length }} 句</p>
      <div class="text-center mb-4">
        <img
          v-if="currentSentence.image"
          :src="currentSentence.image"
          :alt="currentSentence.text"
          class="w-40 h-40 object-cover rounded-2xl mx-auto border-4 border-amber-200"
          @error="imgError($event, currentSentence)"
        />
      </div>
      <div class="text-center mb-4">
        <p class="text-3xl font-bold text-gray-800 mb-2">{{ currentSentence.text }}</p>
        <p class="text-lg text-amber-600">{{ currentSentence.cn }}</p>
        <button @click="speak(currentSentence.text)" class="mt-3 text-5xl hover:scale-110 active:scale-95 transition-transform">🔊</button>
      </div>
      <div class="text-center">
        <button
          v-if="!sentenceDone"
          @click="finishSentence"
          class="px-8 py-4 bg-secondary text-white rounded-full text-xl font-bold hover:bg-opacity-80 transition-all"
        >
          🎤 我读好啦!
        </button>
        <button v-else @click="finishSentenceNext" class="px-8 py-4 bg-primary text-white rounded-full text-xl font-bold hover:bg-opacity-80 transition-all">
          {{ sentenceIsLast ? (stepIndex === steps.length - 1 ? '查看星星 →' : '下一关 →') : '下一句 →' }}
        </button>
      </div>
    </div>

    <!-- ============ 完成庆祝 ============ -->
    <div v-else class="bg-white rounded-3xl p-8 shadow-lg w-full max-w-2xl text-center">
      <p class="text-7xl mb-3 animate-bounce">🎉</p>
      <h2 class="text-3xl font-bold text-gray-800 mb-2">太棒了!</h2>
      <p class="text-gray-600 text-lg mb-5">这节课你完成了所有挑战</p>
      <div class="flex justify-center gap-2 mb-6">
        <span v-for="n in Math.min(stars, 12)" :key="n" class="text-3xl animate-bounce" :style="{ animationDelay: (n * 0.08) + 's' }">⭐</span>
      </div>
      <p class="text-2xl font-bold text-amber-500 mb-6">获得 {{ stars }} 颗星星!</p>
      <p class="text-gray-500 mb-6">{{ praise }}</p>
      <button
        @click="finishLesson"
        class="px-8 py-4 bg-primary text-white rounded-full text-xl font-bold hover:bg-opacity-80 transition-all animate-pulse"
      >
        完成课程 🎉
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { courseApi } from '../api'

const router = useRouter()
const route = useRoute()

const courseId = route.params.courseId
const lessonId = route.params.lessonId

const lessonTitle = ref('')
const steps = ref([])
const stepIndex = ref(0)
const stars = ref(0)
const loading = ref(true)
const loadError = ref(false)

// listen_tap / listen_letter 状态
const listenIndex = ref(0)
const listenAnswered = ref(false)
const listenFeedback = ref('')
const listenWrongSet = ref(new Set())

// look_choose 状态
const lookIndex = ref(0)
const lookAnswered = ref(false)
const lookFeedback = ref('')
const lookWrongSet = ref(new Set())

// sentence 状态
const sentenceIndex = ref(0)
const sentenceDone = ref(false)

// video 状态
const activeVideo = ref(0)

// spell 状态
const spellIndex = ref(0)
const spellBuilt = ref([])
const spellTileUsed = ref([])
const spellAnswered = ref(false)
const spellFeedback = ref('')

const currentStep = computed(() => steps.value[stepIndex.value] || {})
const currentQuestion = computed(() => currentStep.value.questions?.[listenIndex.value] || {})
const currentLook = computed(() => currentStep.value.questions?.[lookIndex.value] || {})
const currentSentence = computed(() => currentStep.value.sentences?.[sentenceIndex.value] || {})
const currentSpell = computed(() => currentStep.value.questions?.[spellIndex.value] || {})

const listenDone = computed(() => {
  const qs = currentStep.value.questions || []
  return qs.length > 0 && listenIndex.value >= qs.length
})
const lookDone = computed(() => {
  const qs = currentStep.value.questions || []
  return qs.length > 0 && lookIndex.value >= qs.length
})
const sentenceStepDone = computed(() => {
  const ss = currentStep.value.sentences || []
  return ss.length > 0 && sentenceIndex.value >= ss.length
})

const sentenceIsLast = computed(() => {
  const ss = currentStep.value.sentences || []
  return sentenceIndex.value >= ss.length - 1
})

const spellTiles = computed(() => {
  const word = currentSpell.value.word || ''
  let letters = word.toLowerCase().split('')
  // 打乱,直到与原顺序不同
  let shuffled = shuffleArray(letters)
  let attempts = 0
  while (shuffled.join('') === word.toLowerCase() && attempts < 10) {
    shuffled = shuffleArray(letters)
    attempts++
  }
  return shuffled
})

const spellDone = computed(() => {
  const qs = currentStep.value.questions || []
  return qs.length > 0 && spellIndex.value >= qs.length
})

const shuffleArray = (arr) => {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

const praise = computed(() => {
  if (stars.value >= 12) return '你是超级英语小达人!'
  if (stars.value >= 8) return '学得又快又准,继续加油!'
  if (stars.value >= 4) return '很不错哦,再多练几遍会更好!'
  return '完成了就是胜利,明天再来挑战吧!'
})

const getUserId = () => parseInt(localStorage.getItem('userId'))

// ---------- 发音(统一模块:原生 TTS 插件 / Web speechSynthesis) ----------
const speak = (text) => {
  import('../lib/tts').then((m) => m.speak(text))
}

const playCurrent = () => speak(currentQuestion.value.audio || currentQuestion.value.target)

// ---------- 学习卡片 ----------
const tapCard = (card) => {
  speak(card.voice || card.word)
}

// ---------- 听音选图 ----------
const answerListen = (word) => {
  if (listenAnswered.value) return
  if (word === currentQuestion.value.target) {
    listenAnswered.value = true
    listenFeedback.value = 'right'
    stars.value++
    setTimeout(() => {
      listenIndex.value++
      listenAnswered.value = false
      listenFeedback.value = ''
      if (!listenDone.value) setTimeout(playCurrent, 400)
    }, 900)
  } else {
    listenFeedback.value = 'wrong'
    setTimeout(() => { listenFeedback.value = '' }, 800)
  }
}

const optionClass = (word) => {
  if (!listenAnswered.value) return 'border-amber-200 bg-amber-50 hover:scale-105 active:scale-95'
  if (word === currentQuestion.value.target) return 'border-green-400 bg-green-50'
  return 'border-gray-200 bg-gray-50 opacity-60'
}

// ---------- 听音选字母(phonics) ----------
const answerLetter = (letter) => {
  if (listenAnswered.value) return
  if (letter === currentQuestion.value.target) {
    listenAnswered.value = true
    listenFeedback.value = 'right'
    stars.value++
    setTimeout(() => {
      listenIndex.value++
      listenAnswered.value = false
      listenFeedback.value = ''
      if (!listenDone.value) setTimeout(playCurrent, 400)
    }, 900)
  } else {
    listenFeedback.value = 'wrong'
    setTimeout(() => { listenFeedback.value = '' }, 800)
  }
}

const letterOptionClass = (letter) => {
  if (!listenAnswered.value) return 'border-gray-200 bg-white hover:border-primary hover:bg-pink-50 active:scale-95'
  if (letter === currentQuestion.value.target) return 'border-green-400 bg-green-50 text-green-700'
  return 'border-gray-200 bg-gray-50 opacity-60'
}

// ---------- 听音拼词(phonics) ----------
const addSpellLetter = (ch, idx) => {
  if (spellTileUsed.value[idx] || spellAnswered.value) return
  spellTileUsed.value[idx] = true
  spellBuilt.value.push(ch)
}

const clearSpell = () => {
  spellBuilt.value = []
  spellTileUsed.value = []
}

const submitSpell = () => {
  if (spellAnswered.value) return
  spellAnswered.value = true
  const word = spellBuilt.value.join('').toLowerCase()
  if (word === (currentSpell.value.word || '').toLowerCase()) {
    spellFeedback.value = 'right'
    stars.value++
    setTimeout(() => {
      spellIndex.value++
      spellBuilt.value = []
      spellTileUsed.value = []
      spellAnswered.value = false
      spellFeedback.value = ''
      if (!spellDone.value) setTimeout(() => speak(currentSpell.value.audio), 400)
    }, 900)
  } else {
    spellFeedback.value = 'wrong'
    setTimeout(() => {
      spellFeedback.value = ''
      spellAnswered.value = false
      spellBuilt.value = []
      spellTileUsed.value = []
    }, 900)
  }
}

// ---------- 看图选词 ----------
const answerLook = (word) => {
  if (lookAnswered.value) return
  if (word === currentLook.value.word) {
    lookAnswered.value = true
    lookFeedback.value = 'right'
    stars.value++
    setTimeout(() => {
      lookIndex.value++
      lookAnswered.value = false
      lookFeedback.value = ''
    }, 900)
  } else {
    lookFeedback.value = 'wrong'
    setTimeout(() => { lookFeedback.value = '' }, 800)
  }
}

const wordClass = (word) => {
  if (!lookAnswered.value) return 'border-gray-200 bg-white hover:border-primary hover:bg-pink-50 active:scale-95'
  if (word === currentLook.value.word) return 'border-green-400 bg-green-50 text-green-700'
  return 'border-gray-200 bg-gray-50 opacity-60'
}

// ---------- 句子跟读 ----------
const finishSentence = () => {
  sentenceDone.value = true
  stars.value++
}

const finishSentenceNext = () => {
  const ss = currentStep.value.sentences || []
  if (sentenceIndex.value < ss.length - 1) {
    sentenceIndex.value++
    sentenceDone.value = false
    setTimeout(() => speak(currentSentence.value.text), 400)
  } else {
    nextStep()
  }
}

// ---------- 步骤推进 ----------
const nextStep = () => {
  // 重置该步骤的临时状态
  listenIndex.value = 0
  listenAnswered.value = false
  listenFeedback.value = ''
  lookIndex.value = 0
  lookAnswered.value = false
  lookFeedback.value = ''
  sentenceIndex.value = 0
  sentenceDone.value = false
  spellIndex.value = 0
  spellBuilt.value = []
  spellTileUsed.value = []
  spellAnswered.value = false
  spellFeedback.value = ''
  activeVideo.value = 0

  if (stepIndex.value < steps.value.length - 1) {
    stepIndex.value++
    const step = currentStep.value
    if ((step.type === 'listen_tap' || step.type === 'listen_letter') && step.questions?.length) {
      setTimeout(playCurrent, 500)
    }
    if (step.type === 'spell' && step.questions?.length) {
      setTimeout(() => speak(currentSpell.value.audio), 500)
    }
  } else {
    stepIndex.value++ // 进入完成页
  }
}

const finishLesson = async () => {
  try {
    await courseApi.completeLesson({
      user_id: getUserId(),
      course_id: parseInt(courseId),
      lesson_id: parseInt(lessonId),
      stars: stars.value,
    })
  } catch {
    // 记录失败不阻塞孩子,直接返回
  }
  router.push(`/courses/${courseId}`)
}

const goBack = () => {
  import('../lib/tts').then((m) => m.stopSpeaking())
  router.push(`/courses/${courseId}`)
}

const imgError = (e, obj) => {
  e.target.style.display = 'none'
}

onMounted(async () => {
  try {
    const res = await courseApi.lessonContent(courseId, lessonId)
    lessonTitle.value = res.data.title
    steps.value = res.data.steps || []
    // 第一步如果是词卡学习,自动读第一个词
    if (steps.value[0]?.type === 'learn') {
      setTimeout(() => {
        const first = steps.value[0].cards?.[0]
        if (first) speak(first.word)
      }, 600)
    }
    if ((steps.value[0]?.type === 'listen_tap' || steps.value[0]?.type === 'listen_letter') && steps.value[0]?.questions?.length) {
      setTimeout(playCurrent, 600)
    }
    if (steps.value[0]?.type === 'spell' && steps.value[0]?.questions?.length) {
      setTimeout(() => speak(currentSpell.value.audio), 600)
    }
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
})
</script>
