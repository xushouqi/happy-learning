// 离线 axios 适配器:拦截 /api/* 请求,全部由本地数据/逻辑处理(安卓离线版)
// 让现有 Vue 页面零改动运行在无后端环境

import * as offline from './data'
import { assembleLessonContent } from './content'

export function installOfflineAdapter(apiInstance) {
  apiInstance.defaults.adapter = async (config) => {
    const method = (config.method || 'get').toLowerCase()
    const url = (config.url || '').replace(/^\/api/, '') // 去掉 baseURL 前缀
    let data = config.data
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch {
        /* keep as-is */
      }
    }
    const result = await route(method, url, data, config.params)
    return { data: result, status: 200, statusText: 'OK', headers: {}, config }
  }
}

async function route(method, url, data, params) {
  // ---------- 用户 ----------
  if (url.startsWith('/users')) {
    if (method === 'get') return offline.getUsers()
    if (method === 'post') return offline.createUser(data.name, data.avatar)
  }
  // ---------- 教材 / 单元(legacy courses 别名) ----------
  if (url.startsWith('/textbooks') || url.startsWith('/courses')) {
    return offline.getTextbooks()
  }
  if (url.startsWith('/units/')) {
    const id = parseInt(url.split('/').pop())
    const tbs = await offline.getTextbooks()
    for (const t of tbs) {
      const u = (t.units || []).find((x) => x.id === id)
      if (u) return u
    }
    return { id, name: '未知单元' }
  }
  // ---------- 课程模块 ----------
  if (url === '/course/lesson-complete') {
    return offline.completeLesson(data)
  }
  if (url.startsWith('/course/progress/')) {
    return offline.getProgressList()
  }
  if (url.startsWith('/course/')) {
    const parts = url.replace('/course/', '').split('/').filter(Boolean)
    if (parts.length === 0) return offline.listCourses(params && params.user_id)
    const courseId = parseInt(parts[0])
    if (parts.length === 1) return offline.getCourse(courseId, params && params.user_id)
    // /course/{id}/lesson/{lessonId}/content
    if (parts.length === 4 && parts[1] === 'lesson' && parts[3] === 'content') {
      const lessonId = parseInt(parts[2])
      const course = await offline.getCourseRaw(courseId)
      if (!course) throw new Error('Course not found')
      const lesson = (course.lessons || []).find((l) => l.id === lessonId)
      if (!lesson) throw new Error('Lesson not found')
      return assembleLessonContent(course, lesson)
    }
    return []
  }
  // ---------- 答题模式(离线版暂不支持,优雅降级为空数据) ----------
  if (url.startsWith('/questions')) {
    if (url.includes('word-to-image')) return {}
    return []
  }
  if (url.startsWith('/scores') || url.startsWith('/progress')) {
    return []
  }
  // 未知接口
  return []
}
