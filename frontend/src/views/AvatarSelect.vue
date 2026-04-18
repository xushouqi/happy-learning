<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-sky-200 via-blue-100 to-green-200">
    <h1 class="text-4xl font-bold text-primary mb-8 animate-bounce">快乐学英语</h1>
    <p class="text-lg text-gray-600 mb-6">选择你的头像开始学习吧！</p>

    <div class="grid grid-cols-3 gap-6">
      <button
        v-for="avatar in avatars"
        :key="avatar.id"
        @click="selectUser(avatar)"
        class="flex flex-col items-center p-6 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all hover:scale-105"
      >
        <span class="text-7xl">{{ avatar.emoji }}</span>
        <span class="mt-3 text-xl font-semibold text-gray-700">{{ avatar.name }}</span>
      </button>
    </div>

    <button
      @click="showAdd = true"
      class="mt-8 px-6 py-3 bg-secondary text-white rounded-full text-lg hover:bg-opacity-80 transition-all"
    >
      + 添加新用户
    </button>

    <!-- Add User Modal -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 m-4 max-w-sm w-full">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">添加新用户</h2>
        <input
          v-model="newName"
          placeholder="输入名字"
          class="w-full px-4 py-2 border-2 border-gray-200 rounded-xl mb-4 text-lg"
        />
        <div class="grid grid-cols-4 gap-2 mb-4">
          <button
            v-for="emoji in avatarOptions"
            :key="emoji"
            @click="newAvatar = emoji"
            :class="['text-3xl p-2 rounded-xl transition-all', newAvatar === emoji ? 'bg-accent scale-110' : 'bg-gray-100']"
          >
            {{ emoji }}
          </button>
        </div>
        <div class="flex gap-3">
          <button @click="showAdd = false" class="flex-1 py-2 bg-gray-200 rounded-xl">取消</button>
          <button @click="addUser" class="flex-1 py-2 bg-primary text-white rounded-xl">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { users as usersApi } from '../api'

const router = useRouter()
const showAdd = ref(false)
const newName = ref('')
const newAvatar = ref('')

const avatars = ref([])
const avatarOptions = ['🐰', '🐱', '🐶', '🐼', '🦊', '🐨', '🐸', '🦄']

onMounted(async () => {
  try {
    const res = await usersApi.list()
    avatars.value = res.data
  } catch {
    avatars.value = []
  }
})

const selectUser = (user) => {
  localStorage.setItem('userId', user.id)
  localStorage.setItem('userName', user.name)
  router.push('/dashboard')
}

const addUser = async () => {
  if (!newName.value || !newAvatar.value) return
  try {
    const res = await usersApi.create({ name: newName.value, avatar: newAvatar.value })
    avatars.value.push(res.data)
    showAdd.value = false
    newName.value = ''
    newAvatar.value = ''
  } catch (e) {
    console.error('Failed to create user', e)
  }
}
</script>
