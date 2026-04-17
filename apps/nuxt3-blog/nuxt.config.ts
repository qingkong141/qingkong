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
      script: [
        {
          innerHTML: `(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&matchMedia('(prefers-color-scheme:dark)').matches))document.documentElement.classList.add('dark')}catch(e){}})()`,
          type: 'text/javascript',
        },
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
        target: 'http://127.0.0.1:18000/qingkong',
        changeOrigin: true,
      },
    },
  },

  runtimeConfig: {
    // 仅服务端使用：SSR 期间直接连接同一 docker 网络中的后端
    // docker-compose.prod.yml 通过 env NUXT_API_INTERNAL 注入
    apiInternal: '',
    public: {
      // 浏览器侧：走 nginx 反代，同源调用
      apiBase: '/qingkong',
    },
  },

  compatibilityDate: '2025-01-01',
})
