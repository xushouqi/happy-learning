// 课程内容离线组装:与后端 app/routers/course_module.py 逻辑一致
// 游戏题随机抽取,图片/视频指向打包资源

import { load } from './data'

function imgUrl(imagePath) {
  if (!imagePath) return null
  return imagePath.startsWith('/') ? imagePath : '/' + imagePath
}

function wordPool(words, unitId, vocabWords) {
  const pool = {}
  if (!words || !words.length) return pool
  for (const v of vocabWords) {
    if (v.unit_id === unitId && words.includes(v.word)) {
      pool[v.word] = {
        word: v.word,
        image: imgUrl(v.image_path),
        sentence: v.example_sentence,
      }
    }
  }
  for (const w of words) {
    if (!pool[w]) pool[w] = { word: w, image: null, sentence: null }
  }
  return pool
}

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function sampleTargets(words, count) {
  return shuffle(words).slice(0, count)
}

function distractors(target, pool, n = 3) {
  return shuffle(Object.keys(pool).filter((w) => w !== target)).slice(0, n)
}

export async function assembleLessonContent(course, lesson) {
  const { vocabWords } = await load()
  const unitId = course.unit_id
  const configSteps = (lesson.content && lesson.content.steps) || []
  const steps = []

  for (const step of configSteps) {
    const stype = step.type
    if (stype === 'story') {
      steps.push({
        type: 'story',
        title: step.title || '',
        text: step.text || '',
        emoji: step.emoji || '📖',
      })
    } else if (stype === 'learn') {
      const words = step.words || []
      const cnMap = step.cn || {}
      const imagesMap = step.images || {}
      const examplesMap = step.examples || {}
      const voicesMap = step.voices || {}
      const pool = wordPool(words, unitId, vocabWords)
      const cards = words.map((w) => {
        let voice = voicesMap[w]
        if (!voice && /^[A-Z]$/.test(w) && examplesMap[w]) {
          voice = examplesMap[w].replace(/ · /g, '. ') + '.'
        }
        return {
          word: w,
          cn: cnMap[w] || '',
          image: imagesMap[w] || pool[w].image,
          sentence: pool[w].sentence,
          examples: examplesMap[w] || '',
          voice: voice || w,
        }
      })
      steps.push({ type: 'learn', title: step.title || '学一学', cards })
    } else if (stype === 'video') {
      const videos = (step.videos || [])
        .filter((v) => v.file)
        .map((v) => ({ label: v.label || '', url: '/videos/' + v.file }))
      steps.push({ type: 'video', title: step.title || '看动画学一学', videos })
    } else if (stype === 'listen_letter') {
      const letters = step.letters || []
      const allLetters = letters.map((x) => x.letter)
      const questions = []
      for (const item of shuffle(letters).slice(0, step.count || 5)) {
        const opts = shuffle([item.letter, ...shuffle(allLetters.filter((l) => l !== item.letter)).slice(0, 3)])
        questions.push({
          target: item.letter,
          audio: item.sample || item.letter,
          options: opts,
        })
      }
      steps.push({ type: 'listen_letter', title: step.title || '听一听,选字母', questions })
    } else if (stype === 'spell') {
      const words = step.words || []
      const questions = shuffle(words)
        .slice(0, step.count || 4)
        .map((w) => ({ word: w, audio: w }))
      steps.push({ type: 'spell', title: step.title || '拼一拼', questions })
    } else if (stype === 'listen_tap') {
      const words = step.words || []
      const voicesMap = step.voices || {}
      const pool = wordPool(words, unitId, vocabWords)
      const questions = sampleTargets(words, step.count || 4).map((target) => {
        const options = shuffle([target, ...distractors(target, pool)])
        return {
          target,
          audio: voicesMap[target] || target,
          options: options.map((o) => ({ word: o, image: pool[o].image })),
        }
      })
      steps.push({ type: 'listen_tap', title: step.title || '听一听,点一点', questions })
    } else if (stype === 'look_choose') {
      const words = step.words || []
      const imagesMap = step.images || {}
      const pool = wordPool(words, unitId, vocabWords)
      const questions = sampleTargets(words, step.count || 4).map((target) => {
        const options = shuffle([target, ...distractors(target, pool)])
        return {
          word: target,
          image: imagesMap[target] || pool[target].image,
          options,
        }
      })
      steps.push({ type: 'look_choose', title: step.title || '看一看,选一选', questions })
    } else if (stype === 'sentence') {
      const sentences = []
      for (const s of step.sentences || []) {
        let image = null
        if (s.word) {
          const pool = wordPool([s.word], unitId, vocabWords)
          image = pool[s.word] ? pool[s.word].image : null
        }
        sentences.push({ text: s.text || '', cn: s.cn || '', image })
      }
      steps.push({ type: 'sentence', title: step.title || '句子跟读', sentences })
    }
  }

  return {
    lesson_id: lesson.id,
    course_id: course.id,
    title: lesson.title,
    subtitle: lesson.subtitle,
    steps,
  }
}
