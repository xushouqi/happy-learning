import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:9000',
        changeOrigin: true,
      },
      '/muzzy_word_cards': {
        target: 'http://localhost:9000',
        changeOrigin: true,
      },
      '/yakka_dee': {
        target: 'http://localhost:9000',
        changeOrigin: true,
      },
    },
  },
})
