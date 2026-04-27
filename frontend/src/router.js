import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('./views/AvatarSelect.vue') },
  { path: '/dashboard', name: 'dashboard', component: () => import('./views/Dashboard.vue') },
  { path: '/progress', name: 'progress', component: () => import('./views/Progress.vue') },
  { path: '/calendar', name: 'calendar', component: () => import('./views/Calendar.vue') },
  { path: '/wrongbook', name: 'wrongbook', component: () => import('./views/WrongBook.vue') },
  { path: '/quiz/wrong', name: 'quizWrong', component: () => import('./views/Quiz.vue') },
  { path: '/video/:unitId', name: 'video', component: () => import('./views/VideoPlayer.vue') },
  { path: '/quiz-type/:unitId', name: 'quizType', component: () => import('./views/QuizTypeSelect.vue') },
  { path: '/quiz/:unitId', name: 'quiz', component: () => import('./views/Quiz.vue') },
  { path: '/results', name: 'results', component: () => import('./views/Results.vue') },
  { path: '/speech-practice', name: 'speechPractice', component: () => import('./views/SpeechPractice.vue') },
  { path: '/speech-quiz/:unitId', name: 'speechQuiz', component: () => import('./views/SpeechQuiz.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
