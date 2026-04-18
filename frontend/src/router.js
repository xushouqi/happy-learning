import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('./views/AvatarSelect.vue') },
  { path: '/dashboard', name: 'dashboard', component: () => import('./views/Dashboard.vue') },
  { path: '/progress', name: 'progress', component: () => import('./views/Progress.vue') },
  { path: '/video/:unitId', name: 'video', component: () => import('./views/VideoPlayer.vue') },
  { path: '/quiz/:unitId', name: 'quiz', component: () => import('./views/Quiz.vue') },
  { path: '/results', name: 'results', component: () => import('./views/Results.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
