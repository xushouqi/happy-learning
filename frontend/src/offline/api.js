// 离线 axios 适配器:拦截 /api/* 请求,全部由本地数据/逻辑处理(安卓离线版)
// 让现有 Vue 页面零改动运行在无后端环境

import * as offline from './data'
import * as quiz from './quiz'
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
  // ---------- 答题模式(离线版) ----------
  if (url.startsWith('/questions')) {
    // /questions/types/{unitId}
    let m = url.match(/^\/questions\/types\/(\d+)/)
    if (m) return quiz.getTypes(parseInt(m[1]))
    // /questions/quiz/{unitId}?question_types=
    m = url.match(/^\/questions\/quiz\/(\d+)/)
    if (m) return quiz.getQuiz(parseInt(m[1]), params && params.question_types)
    // /questions/by-ids?ids=
    if (url.includes('/by-ids')) return quiz.getByIds(params && params.ids)
    // /questions/word-to-image
    if (url.includes('word-to-image')) return quiz.getWordToImage()
    // /questions/speech-practice/{unitId}
    m = url.match(/^\/questions\/speech-practice\/(\d+)/)
    if (m) return []
    // /questions/random
    if (url.includes('/random')) return quiz.getRandom(params)
    // /questions/textbook/{id}
    m = url.match(/^\/questions\/textbook\/(\d+)/)
    if (m) return quiz.getByTextbook(parseInt(m[1]))
    // /questions/unit/{unitId}
    m = url.match(/^\/questions\/unit\/(\d+)/)
    if (m) return quiz.getByUnit(parseInt(m[1]))
    // /questions/{id}
    m = url.match(/^\/questions\/(\d+)/)
    if (m) return quiz.getById(parseInt(m[1]))
    return []
  }
  // ---------- 成绩 / 进度(离线版) ----------
  if (url.startsWith('/scores')) {
    if (url === '/scores/' && method === 'post') return quiz.recordScore(data)
    // /scores/unit-complete (POST, query 参数)
    if (url.includes('/unit-complete')) {
      return quiz.recordUnitComplete({
        user_id: params && params.user_id,
        unit_id: params && params.unit_id,
        score: params && params.score,
        total: params && params.total,
      })
    }
    // /scores/user/{id}/wrong-questions/quiz
    if (url.includes('/wrong-questions/quiz')) {
      const uid = parseInt(url.split('/')[3])
      return quiz.wrongQuiz(uid)
    }
    // /scores/user/{id}/wrong-questions
    if (url.includes('/wrong-questions')) {
      const uid = parseInt(url.split('/')[3])
      return quiz.wrongQuestions(uid)
    }
    // /scores/user/{id}/type-stats
    if (url.includes('/type-stats')) {
      const uid = parseInt(url.split('/')[3])
      return quiz.typeStats(uid)
    }
    // /scores/user/{id}/unit/{unitId} (DELETE)
    if (method === 'delete') {
      const parts = url.split('/').filter(Boolean) // scores/user/{id}/unit/{unitId}
      return quiz.clearUnit(parseInt(parts[2]), parseInt(parts[4]))
    }
    // /scores/user/{id}
    const parts = url.split('/').filter(Boolean)
    if (parts.length >= 3 && parts[0] === 'scores' && parts[1] === 'user') {
      return quiz.listScores(parseInt(parts[2]))
    }
    return []
  }
  if (url.startsWith('/progress')) {
    // /progress/user/{id}/textbooks
    if (url.includes('/textbooks')) {
      const uid = parseInt(url.split('/')[3])
      return quiz.progressByCourse(uid)
    }
    // /progress/user/{id}/calendar
    if (url.includes('/calendar')) {
      const uid = parseInt(url.split('/')[3])
      return quiz.progressByUser(uid)
    }
    // /progress/user/{id}
    const parts = url.split('/').filter(Boolean)
    if (parts.length >= 3 && parts[0] === 'progress' && parts[1] === 'user') {
      return quiz.progressByUser(parseInt(parts[2]))
    }
    // POST /progress/
    if (url === '/progress/' && method === 'post') {
      return { ...data, id: 1 }
    }
    return []
  }
  // 未知接口
  return []
}
