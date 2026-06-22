import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? '/admin/' : '/',
  plugins: [vue()],
  server: {
    port: 3000,
    hmr: { overlay: false },
    proxy: {
      '/yunpan': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
}))
