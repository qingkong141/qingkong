import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/qingkong': {
        target: 'http://127.0.0.1:18000',
        changeOrigin: true,
      },
    },
  },
})
