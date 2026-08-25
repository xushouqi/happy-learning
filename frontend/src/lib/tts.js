// 统一发音模块 v2:
// 1. 优先播放预生成的 edge-tts 神经网络音频(/audio/*.mp3,音质自然流畅)
// 2. 无预生成音频时:原生环境用 Capacitor TTS 插件,Web 回退 speechSynthesis

import { Capacitor } from '@capacitor/core'
import { TextToSpeech } from '@capacitor-community/text-to-speech'
import { AUDIO_MAP } from '../offline/audio-map'

let currentAudio = null

function normText(text) {
  return String(text).trim().toLowerCase().replace(/\s+/g, ' ')
}

function playFile(file) {
  return new Promise((resolve) => {
    try {
      if (currentAudio) {
        currentAudio.pause()
        currentAudio = null
      }
      const a = new Audio('/audio/' + file)
      currentAudio = a
      a.play().then(resolve).catch(() => resolve(false))
    } catch {
      resolve(false)
    }
  })
}

export async function speak(text, opts = {}) {
  if (!text) return
  const { rate = 0.8, lang = 'en-US' } = opts

  // 预生成高质量音频(edge-tts 神经网络语音)
  const key = normText(text)
  const file = AUDIO_MAP[key]
  if (file) {
    const ok = await playFile(file)
    if (ok) return
  }

  // 原生 App 环境:系统 TTS 引擎
  if (Capacitor.isNativePlatform()) {
    try {
      await TextToSpeech.speak({ text, lang, rate })
      return
    } catch (e) {
      console.warn('native TTS failed, fallback to speechSynthesis:', e)
    }
  }

  // Web / 回退
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = lang
  u.rate = rate
  u.pitch = 1.05
  const voices = window.speechSynthesis.getVoices()
  const v = voices.find((x) => x.lang.toLowerCase().startsWith('en') && /microsoft|google|samantha|aria/i.test(x.name))
  if (v) u.voice = v
  window.speechSynthesis.speak(u)
}

export function stopSpeaking() {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio = null
  }
  try {
    if (Capacitor.isNativePlatform()) {
      TextToSpeech.stop()
    }
  } catch {
    /* ignore */
  }
  if ('speechSynthesis' in window) window.speechSynthesis.cancel()
}
