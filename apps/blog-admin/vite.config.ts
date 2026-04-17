import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? '/blog-admin/' : '/',
  plugins: [
    vue(),
    qiankun('blog-admin', { useDevMode: true }),
  ],
  server: {
    port: 3001,
    cors: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    proxy: {
      '/qingkong': {
        target: 'http://127.0.0.1:18000',
        changeOrigin: true,
      },
    },
  },
}))
