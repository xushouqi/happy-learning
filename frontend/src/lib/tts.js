// 统一发音模块:原生环境用 Capacitor TTS 插件(系统引擎,安卓 WebView speechSynthesis 不可靠),
// Web 环境回退 speechSynthesis

import { Capacitor } from '@capacitor/core'
import { TextToSpeech } from '@capacitor-community/text-to-speech'

export async function speak(text, opts = {}) {
  if (!text) return
  const { rate = 0.8, lang = 'en-US' } = opts

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
  try {
    if (Capacitor.isNativePlatform()) {
      TextToSpeech.stop()
    }
  } catch {
    /* ignore */
  }
  if ('speechSynthesis' in window) window.speechSynthesis.cancel()
}
