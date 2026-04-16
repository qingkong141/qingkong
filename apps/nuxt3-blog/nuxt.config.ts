export default defineNuxtConfig({
  devtools: { enabled: false },

  modules: [],

  app: {
    head: {
      title: '青空 QingKong',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '青空博客 — 记录技术与生活' },
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap',
        },
      ],
    },
  },

  css: ['~/assets/css/main.css'],

  nitro: {
    devProxy: {
      '/qingkong': {
        target: 'http://127.0.0.1:8000/qingkong',
        changeOrigin: true,
      },
    },
  },

  runtimeConfig: {
    public: {
      apiBase: '/qingkong',
    },
  },

  compatibilityDate: '2025-01-01',
})
