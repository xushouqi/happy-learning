<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-200 via-blue-100 to-green-200 flex flex-col items-center justify-center p-4">
    <!-- Stars animation -->
    <div class="text-6xl mb-4 animate-bounce">🌟</div>

    <h1 class="text-3xl font-bold text-primary mb-6">练习完成！</h1>

    <!-- Score Circle -->
    <div class="bg-white rounded-full p-8 shadow-lg mb-6">
      <div class="text-center">
        <span class="text-5xl font-bold text-secondary">{{ percentage }}%</span>
        <p class="text-gray-500 mt-2">正确率</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="bg-white rounded-2xl p-6 shadow-lg w-full max-w-sm mb-6">
      <div class="flex justify-between items-center mb-3">
        <span class="text-gray-600">答对</span>
        <span class="text-2xl text-green-500">✅ {{ correctCount }}</span>
      </div>
      <div class="flex justify-between items-center mb-3">
        <span class="text-gray-600">答错</span>
        <span class="text-2xl text-red-500">❌ {{ wrongCount }}</span>
      </div>
      <div class="flex justify-between items-center">
        <span class="text-gray-600">星星</span>
        <span class="text-2xl">⭐ {{ totalCount }}</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex gap-4">
      <button
        @click="router.push('/dashboard')"
        class="px-6 py-3 bg-secondary text-white rounded-full text-lg hover:bg-opacity-80 transition-all"
      >
        返回首页
      </button>
      <button
        @click="router.push(`/quiz/${route.query.unitId}`)"
        class="px-6 py-3 bg-primary text-white rounded-full text-lg hover:bg-opacity-80 transition-all"
      >
        再来一次
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const totalCount = computed(() => parseInt(route.query.total) || 0)
const questionCount = computed(() => parseInt(route.query.count) || 1)
const correctCount = computed(() => totalCount.value)
const wrongCount = computed(() => questionCount.value - totalCount.value)
const percentage = computed(() => Math.round((totalCount.value / questionCount.value) * 100))
</script>
