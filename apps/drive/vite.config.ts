import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

export default defineConfig({
  plugins: [
    vue(),
    qiankun('drive', { useDevMode: true }),
  ],
  server: {
    port: 3002,
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
})
