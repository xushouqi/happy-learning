// 答题模式离线实现:题库查询/出题逻辑 + 成绩与进度记录(localStorage)
// 逻辑与后端 app/routers/questions.py、scores.py 对齐

import { load, safeGet, safeSet } from './data'

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// ---------- 题目查询 ----------
export async function getTypes(unitId) {
  const { questions } = await load()
  const types = [...new Set(questions.filter((q) => q.unit_id === unitId).map((q) => q.type))]
  return { types }
}

export async function getQuiz(unitId, questionTypes) {
  const { questions } = await load()
  const unitQs = questions.filter((q) => q.unit_id === unitId)
  const existingTypes = [...new Set(unitQs.map((q) => q.type))]
  let typesToUse
  if (questionTypes) {
    const requested = String(questionTypes).split(',').map((t) => t.trim()).filter(Boolean)
    typesToUse = requested.filter((t) => existingTypes.includes(t))
  } else {
    typesToUse = existingTypes
  }
  let result = []
  if (typesToUse.length === 1) {
    result = shuffle(unitQs.filter((q) => q.type === typesToUse[0]))
  } else {
    for (const t of typesToUse) {
      result = result.concat(shuffle(unitQs.filter((q) => q.type === t)).slice(0, 10))
    }
  }
  return shuffle(result)
}

export async function getByUnit(unitId) {
  const { questions } = await load()
  return questions.filter((q) => q.unit_id === unitId)
}

export async function getByTextbook(textbookId) {
  const { questions } = await load()
  return questions.filter((q) => q.textbook_id === textbookId)
}

export async function getRandom(params) {
  const { questions } = await load()
  let list = questions
  if (params && params.textbook_id) list = list.filter((q) => q.textbook_id === parseInt(params.textbook_id))
  if (params && params.unit_id) list = list.filter((q) => q.unit_id === parseInt(params.unit_id))
  if (params && params.question_type) list = list.filter((q) => q.type === params.question_type)
  return shuffle(list).slice(0, parseInt(params && params.count) || 10)
}

export async function getByIds(ids) {
  const { questions } = await load()
  const idList = String(ids).split(',').map((x) => parseInt(x))
  return questions.filter((q) => idList.includes(q.id))
}

export async function getById(id) {
  const { questions } = await load()
  return questions.find((q) => q.id === parseInt(id))
}

export async function getWordToImage() {
  const { vocabWords } = await load()
  const map = {}
  for (const v of vocabWords) {
    if (v.image_path) map[v.word.toLowerCase()] = '/' + v.image_path
  }
  return map
}

// ---------- 成绩记录 ----------
const SCORES_KEY = 'offline_scores'
const UNIT_PROG_KEY = 'offline_unit_progress'
const DAILY_KEY = 'offline_daily'

function getScores() {
  try {
    return JSON.parse(safeGet(SCORES_KEY)) || []
  } catch {
    return []
  }
}
function setScores(list) {
  safeSet(SCORES_KEY, JSON.stringify(list))
}
function getUnitProg() {
  try {
    return JSON.parse(safeGet(UNIT_PROG_KEY)) || {}
  } catch {
    return {}
  }
}
function setUnitProg(map) {
  safeSet(UNIT_PROG_KEY, JSON.stringify(map))
}
function getDaily() {
  try {
    return JSON.parse(safeGet(DAILY_KEY)) || {}
  } catch {
    return {}
  }
}
function setDaily(map) {
  safeSet(DAILY_KEY, JSON.stringify(map))
}

export function recordScore({ user_id, question_id, correct, score }) {
  const scores = getScores()
  scores.push({
    id: scores.length ? Math.max(...scores.map((s) => s.id)) + 1 : 1,
    user_id,
    question_id,
    correct: !!correct,
    score: score || 0,
    created_at: new Date().toISOString(),
  })
  setScores(scores)
  return scores[scores.length - 1]
}

export function recordUnitComplete({ user_id, unit_id, score, total }) {
  const now = new Date()
  const today = now.toISOString().slice(0, 10)
  const prog = getUnitProg()
  const key = user_id + ':' + unit_id
  const prev = prog[key] || {}
  prog[key] = {
    user_id,
    unit_id,
    best_score: Math.max(prev.best_score || 0, score || 0),
    total_questions: total || 0,
    attempts: (prev.attempts || 0) + 1,
    last_attempt: now.toISOString(),
    completed: true,
  }
  setUnitProg(prog)

  const daily = getDaily()
  const dkey = user_id + ':' + today + ':' + unit_id
  const dprev = daily[dkey] || {}
  daily[dkey] = {
    user_id,
    unit_id,
    date: today,
    total_score: Math.max(dprev.total_score || 0, score || 0),
    completed: true,
  }
  setDaily(daily)
  return { success: true, attempts: prog[key].attempts, best_score: prog[key].best_score }
}

export function listScores(userId) {
  return getScores().filter((s) => s.user_id === parseInt(userId))
}

export function wrongQuestions(userId) {
  const scores = getScores().filter((s) => s.user_id === parseInt(userId))
  // 每题最后一次
  const latest = {}
  for (const s of scores) latest[s.question_id] = s
  const wrongIds = Object.keys(latest).map(Number).filter((id) => !latest[id].correct)
  if (!wrongIds.length) return []
  return getByIds(wrongIds.join(',')).then((questions) =>
    questions.map((q) => ({ ...q, wrong_count: 1 }))
  )
}

export async function wrongQuiz(userId) {
  const wrongs = await wrongQuestions(userId)
  return { question_ids: wrongs.map((q) => q.id) }
}

export function clearUnit(userId, unitId) {
  const scores = getScores()
  setScores(scores.filter((s) => !(s.user_id === parseInt(userId) && s.question_id === undefined)))
  // 通过题目归属清掉该单元分数
  const prog = getUnitProg()
  delete prog[userId + ':' + unitId]
  setUnitProg(prog)
  const daily = getDaily()
  for (const k of Object.keys(daily)) {
    if (k.startsWith(userId + ':') && k.endsWith(':' + unitId)) delete daily[k]
  }
  setDaily(daily)
  return { success: true }
}

export async function typeStats(userId) {
  const scores = getScores().filter((s) => s.user_id === parseInt(userId))
  const { questions } = await load()
  const qMap = Object.fromEntries(questions.map((q) => [q.id, q]))
  const stats = {}
  for (const s of scores) {
    const q = qMap[s.question_id]
    if (!q) continue
    const key = q.unit_id + ':' + q.type
    if (!stats[q.unit_id]) stats[q.unit_id] = {}
    const t = stats[q.unit_id]
    if (!t[q.type]) t[q.type] = { correct: 0, total: 0, wrong: 0 }
    t[q.type].total++
    if (s.correct) t[q.type].correct++
    else t[q.type].wrong++
  }
  return stats
}

// ---------- 进度 ----------
export function progressByUser(userId) {
  const daily = getDaily()
  const out = []
  for (const [k, v] of Object.entries(daily)) {
    if (k.startsWith(userId + ':')) out.push(v)
  }
  return out
}

export async function progressByCourse(userId) {
  const { textbooks, questions } = await load()
  const prog = getUnitProg()
  const units = {}
  for (const tb of textbooks) for (const u of tb.units) units[u.id] = { tb, u }
  const result = []
  for (const tb of textbooks) {
    const tbUnits = tb.units || []
    const unitProgList = []
    let tbBest = 0
    let tbTotal = 0
    let tbUnitsDone = 0
    for (const u of tbUnits) {
      const p = prog[userId + ':' + u.id]
      unitProgList.push({
        id: u.id,
        name: u.name,
        order: u.order,
        completed: !!(p && p.completed),
        best_score: p ? p.best_score || 0 : 0,
        total_questions: p ? p.total_questions || 0 : 0,
        attempts: p ? p.attempts || 0 : 0,
        last_attempt: p ? p.last_attempt : null,
      })
      if (p && p.completed) {
        tbBest += p.best_score || 0
        tbTotal += p.total_questions || 0
        tbUnitsDone++
      }
    }
    result.push({
      id: tb.id,
      name: tb.name,
      total_units: tbUnits.length,
      completed_units: tbUnitsDone,
      best_score: tbBest,
      total_questions: tbTotal,
      units: unitProgList,
    })
  }
  return result
}
