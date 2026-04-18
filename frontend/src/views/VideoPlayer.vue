<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 p-4">
    <header class="flex items-center justify-between mb-6">
      <button @click="router.back()" class="text-3xl hover:scale-110 transition-transform">←</button>
      <h1 class="text-xl font-bold text-gray-800">{{ unitName }}</h1>
      <span class="w-8"></span>
    </header>

    <!-- Video player -->
    <div v-if="videoUrl" class="bg-black rounded-2xl overflow-hidden shadow-lg max-w-3xl mx-auto">
      <video
        ref="videoRef"
        class="w-full"
        controls
        autoplay
        @ended="videoEnded = true"
      >
        <source :src="videoUrl" type="video/mp4" />
        你的浏览器不支持视频播放
      </video>
    </div>

    <!-- No video placeholder -->
    <div v-else class="bg-white rounded-2xl p-8 shadow-lg max-w-3xl mx-auto text-center">
      <span class="text-5xl mb-4">📺</span>
      <p class="text-gray-600">暂无视频</p>
    </div>

    <div class="text-center mt-6">
      <button
        @click="startQuiz"
        class="px-8 py-4 rounded-full text-xl font-bold bg-primary text-white hover:bg-opacity-80 transition-all animate-pulse"
      >
        开始答题 →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { units as unitsApi } from '../api'

const route = useRoute()
const router = useRouter()
const videoRef = ref(null)
const videoEnded = ref(false)
const unitName = ref('学习中')

// Video files mapped from F drive via symlinks
const videoFiles = {
  // Big Muzzy: unit IDs 1-12 → episodes 01-12
  1: 'big_muzzy_ep01.mp4',
  2: 'big_muzzy_ep02.mp4',
  3: 'big_muzzy_ep03.mp4',
  4: 'big_muzzy_ep04.mp4',
  5: 'big_muzzy_ep05.mp4',
  6: 'big_muzzy_ep06.mp4',
  7: 'big_muzzy_ep07.mp4',
  8: 'big_muzzy_ep08.mp4',
  9: 'big_muzzy_ep09.mp4',
  10: 'big_muzzy_ep10.mp4',
  11: 'big_muzzy_ep11.mp4',
  12: 'big_muzzy_ep12.mp4',
}

const videoUrl = computed(() => {
  const unitId = parseInt(route.params.unitId)
  const file = videoFiles[unitId]
  return file ? `/api/media/video/${encodeURIComponent(file)}` : ''
})

onMounted(async () => {
  try {
    const res = await unitsApi.get(parseInt(route.params.unitId))
    unitName.value = res.data.name
  } catch {}
  if (videoRef.value && videoUrl.value) {
    videoRef.value.play().catch(() => {})
  }
})

const startQuiz = () => {
  router.push(`/quiz/${route.params.unitId}`)
}
</script>
