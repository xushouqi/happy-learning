import axios from 'axios'
import { installOfflineAdapter } from '../offline/api'

const api = axios.create({
  baseURL: '/api',
})

// 安卓离线版:启用本地数据适配层(构建时设置 VITE_OFFLINE=true)
if (import.meta.env.VITE_OFFLINE === 'true') {
  installOfflineAdapter(api)
}

export default api

export const users = {
  list: () => api.get('/users/'),
  create: (data) => api.post('/users/', data),
  get: (id) => api.get(`/users/${id}`),
}

export const textbooks = {
  list: () => api.get('/textbooks/'),
  get: (id) => api.get(`/textbooks/${id}`),
}

// Legacy alias - courses are now textbooks
export const courses = textbooks

export const units = {
  get: (id) => api.get(`/units/${id}`),
  create: (data) => api.post('/units/', data),
}

export const questions = {
  byUnit: (unitId) => api.get(`/questions/unit/${unitId}`),
  quiz: (unitId, types) => api.get(`/questions/quiz/${unitId}`, { params: { question_types: types } }),
  types: (unitId) => api.get(`/questions/types/${unitId}`),
  byTextbook: (textbookId) => api.get(`/questions/textbook/${textbookId}`),
  random: (params) => api.get('/questions/random', { params }),
  create: (data) => api.post('/questions/', data),
  wordToImage: () => api.get('/questions/word-to-image'),
  byIds: (ids) => api.get('/questions/by-ids', { params: { ids: ids.join(',') } }),
}

export const scores = {
  record: (data) => api.post('/scores/', data),
  byUser: (userId) => api.get(`/scores/user/${userId}`),
  recordUnitComplete: (data) => api.post('/scores/unit-complete', null, { params: data }),
  wrongQuestions: (userId) => api.get(`/scores/user/${userId}/wrong-questions`),
  wrongQuiz: (userId) => api.get(`/scores/user/${userId}/wrong-questions/quiz`),
  clearUnit: (userId, unitId) => api.delete(`/scores/user/${userId}/unit/${unitId}`),
  typeStats: (userId) => api.get(`/scores/user/${userId}/type-stats`),
}

export const progress = {
  record: (data) => api.post('/progress/', data),
  byUser: (userId) => api.get(`/progress/user/${userId}`),
  byCourse: (userId) => api.get(`/progress/user/${userId}/textbooks`),
  calendar: (userId, year, month) => api.get(`/progress/user/${userId}/calendar`, { params: { year, month } }),
}

// 课程模块
export const courseApi = {
  list: (userId) => api.get('/course/', { params: userId ? { user_id: userId } : {} }),
  get: (id, userId) => api.get(`/course/${id}`, { params: userId ? { user_id: userId } : {} }),
  lessonContent: (courseId, lessonId) => api.get(`/course/${courseId}/lesson/${lessonId}/content`),
  completeLesson: (data) => api.post('/course/lesson-complete', data),
  progress: (userId) => api.get(`/course/progress/${userId}`),
}

