// 统一发音模块 v2.1:
// 1. 优先播放预生成的 edge-tts 神经网络音频(/audio/*.mp3)
// 2. 无预生成音频/播放被拒时:原生环境用 Capacitor TTS 插件,Web 回退 speechSynthesis
// 关键:stopSpeaking 与 audio.play() 必须同步执行(保持用户手势上下文),
//      否则被浏览器自动播放策略拒绝(NotAllowedError)导致 mp3 与 TTS 重复播放

import { Capacitor } from '@capacitor/core'
import { TextToSpeech } from '@capacitor-community/text-to-speech'
import { AUDIO_MAP } from '../offline/audio-map'

let currentAudio = null

function normText(text) {
  return String(text).trim().toLowerCase().replace(/\s+/g, ' ')
}

// 同步停止所有声音(不 await,避免打断用户手势上下文)
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

// 同步触发音频播放(处于用户手势同步栈,规避自动播放策略)
function startPlayFile(file) {
  try {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio = null
    }
    const a = new Audio('/audio/' + file)
    currentAudio = a
    const p = a.play()
    if (p && typeof p.then === 'function') {
      p.catch(() => {
        /* 被自动播放策略拒绝时不阻塞,后续回退由 speak 处理 */
      })
    }
    return true
  } catch {
    return false
  }
}

export async function speak(text, opts = {}) {
  if (!text) return
  stopSpeaking()
  const { rate = 0.8, lang = 'en-US' } = opts

  // 预生成高质量音频(同步触发,保持在用户手势栈内)
  const key = normText(text)
  const file = AUDIO_MAP[key]
  if (file && startPlayFile(file)) return

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
