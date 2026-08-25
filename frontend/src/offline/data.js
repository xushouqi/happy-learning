// 离线数据加载:从打包进应用的 JSON 读取教材/课程/单词/用户
// 用于安卓离线版(无后端),Web 版不使用

let cache = null

export async function load() {
  if (cache) return cache
  const base = '/data/'
  const [textbooks, courses, vocabWords, users] = await Promise.all([
    fetch(base + 'textbooks.json').then((r) => r.json()),
    fetch(base + 'courses.json').then((r) => r.json()),
    fetch(base + 'vocab_words.json').then((r) => r.json()),
    fetch(base + 'users.json').then((r) => r.json()),
  ])
  cache = { textbooks, courses, vocabWords, users }
  return cache
}

// 本地用户列表(服务端 users + 本地新增)
const LOCAL_USERS_KEY = 'offline_users'
function getLocalUsers() {
  try {
    return JSON.parse(localStorage.getItem(LOCAL_USERS_KEY)) || []
  } catch {
    return []
  }
}
function saveLocalUsers(list) {
  localStorage.setItem(LOCAL_USERS_KEY, JSON.stringify(list))
}

export async function getUsers() {
  const { users } = await load()
  return [...users, ...getLocalUsers()]
}

export async function createUser(name, avatar) {
  const { users } = await load()
  const local = getLocalUsers()
  const nextId = Math.max(...users.map((u) => u.id), ...local.map((u) => u.id), 0) + 1
  const user = { id: nextId, name, avatar, created_at: new Date().toISOString() }
  local.push(user)
  saveLocalUsers(local)
  return user
}

export async function getTextbooks() {
  const { textbooks } = await load()
  return textbooks
}

export async function getCourseRaw(courseId) {
  const { courses } = await load()
  return courses.find((c) => c.id === courseId)
}

// ---------- 上课进度(localStorage) ----------
const PROGRESS_KEY = 'offline_course_progress' // { [lessonId]: { stars, completed } }
function getProgress() {
  try {
    return JSON.parse(localStorage.getItem(PROGRESS_KEY)) || {}
  } catch {
    return {}
  }
}
function setProgress(progress) {
  localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress))
}

function aggregate(course, progress) {
  const lessons = course.lessons || []
  let completed = 0
  let stars = 0
  for (const l of lessons) {
    const p = progress[l.id]
    if (p && p.completed) {
      completed++
      stars += p.stars || 0
    }
  }
  return {
    completed_lessons: completed,
    total_stars: stars,
    lesson_count: lessons.length,
  }
}

export async function listCourses(userId) {
  const { courses, textbooks } = await load()
  const progress = getProgress()
  const tbMap = Object.fromEntries(textbooks.map((t) => [t.id, t]))
  return courses
    .filter((c) => c.status === 'active')
    .sort((a, b) => a.order - b.order || a.id - b.id)
    .map((c) => {
      const agg = aggregate(c, progress)
      const tb = tbMap[c.textbook_id] || {}
      return {
        id: c.id,
        textbook_id: c.textbook_id,
        unit_id: c.unit_id,
        title: c.title,
        description: c.description,
        cover_emoji: c.cover_emoji,
        order: c.order,
        status: c.status,
        unit_name: (tb.units || []).find((u) => u.id === c.unit_id)?.name || null,
        textbook_name: tb.name || null,
        lesson_count: agg.lesson_count,
        completed_lessons: agg.completed_lessons,
        total_stars: agg.total_stars,
      }
    })
}

export async function getCourse(courseId, userId) {
  const { courses, textbooks } = await load()
  const course = courses.find((c) => c.id === courseId)
  if (!course) return null
  const progress = getProgress()
  const tb = textbooks.find((t) => t.id === course.textbook_id) || {}
  const agg = aggregate(course, progress)
  return {
    id: course.id,
    textbook_id: course.textbook_id,
    unit_id: course.unit_id,
    title: course.title,
    description: course.description,
    cover_emoji: course.cover_emoji,
    order: course.order,
    status: course.status,
    unit_name: (tb.units || []).find((u) => u.id === course.unit_id)?.name || null,
    textbook_name: tb.name || null,
    lesson_count: agg.lesson_count,
    completed_lessons: agg.completed_lessons,
    total_stars: agg.total_stars,
    lessons: (course.lessons || []).map((l) => {
      const p = progress[l.id]
      return {
        id: l.id,
        title: l.title,
        subtitle: l.subtitle,
        order: l.order,
        completed: !!(p && p.completed),
        stars: p ? p.stars || 0 : 0,
      }
    }),
  }
}

export function completeLesson(payload) {
  const progress = getProgress()
  const prev = progress[payload.lesson_id] || { stars: 0, completed: false }
  progress[payload.lesson_id] = {
    stars: Math.max(prev.stars, payload.stars || 0),
    completed: true,
  }
  setProgress(progress)
  return { success: true, stars: progress[payload.lesson_id].stars, completed: true }
}

export function getProgressList() {
  const progress = getProgress()
  return Object.entries(progress).map(([lessonId, p]) => ({
    course_id: null,
    lesson_id: parseInt(lessonId),
    stars: p.stars,
    completed: p.completed,
    completed_at: null,
  }))
}
