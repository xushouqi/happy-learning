import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

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
  quiz: (unitId) => api.get(`/questions/quiz/${unitId}`),
  byTextbook: (textbookId) => api.get(`/questions/textbook/${textbookId}`),
  random: (params) => api.get('/questions/random', { params }),
  create: (data) => api.post('/questions/', data),
  wordToImage: () => api.get('/questions/word-to-image'),
}

export const scores = {
  record: (data) => api.post('/scores/', data),
  byUser: (userId) => api.get(`/scores/user/${userId}`),
  recordUnitComplete: (data) => api.post('/scores/unit-complete', null, { params: data }),
}

export const progress = {
  record: (data) => api.post('/progress/', data),
  byUser: (userId) => api.get(`/progress/user/${userId}`),
  byCourse: (userId) => api.get(`/progress/user/${userId}/textbooks`),
}
