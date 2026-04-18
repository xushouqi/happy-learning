import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    allowedHosts: ['.ngrok-free.dev'],
    proxy: {
      '/api': {
        target: 'http://localhost:9000',
        changeOrigin: true,
      },
      '/word-cards': {
        target: 'http://localhost:9000',
        changeOrigin: true,
      },
      '/phonics': {
        target: 'http://localhost:9000',
        changeOrigin: true,
      },
      '/muzzy_word_cards': {
        target: 'http://localhost:9000',
        changeOrigin: true,
      },
    },
  },
})
