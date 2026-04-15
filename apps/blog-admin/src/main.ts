import { createApp, type App as VueApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import { renderWithQiankun, qiankunWindow } from 'vite-plugin-qiankun/dist/helper'
import AppComponent from './App.vue'
import { routes } from './router'

let app: VueApp

function createVueApp(base = '/') {
  const router = createRouter({
    history: createWebHistory(base),
    routes,
  })

  app = createApp(AppComponent)
  app.use(createPinia())
  app.use(router)
  return { app, router }
}

// ── qiankun 生命周期 ──────────────────────────────────────────
renderWithQiankun({
  // 应用首次加载时执行一次
  bootstrap() {},

  // 每次激活（挂载）时执行
  mount(props) {
    const { app: vueApp } = createVueApp('/admin/blog')
    // props.container 是 qiankun 为子应用创建的 DOM 容器
    const container = (props as { container?: HTMLElement }).container
    vueApp.mount(container ? container.querySelector('#app')! : '#app')
  },

  // 切走时卸载
  unmount() {
    app?.unmount()
  },

  update() {},
})

// ── 独立运行模式（直接访问 localhost:8081）──────────────────
if (!qiankunWindow.__POWERED_BY_QIANKUN__) {
  // standalone 直接访问 localhost:8081/ ，base 用 /
  const { app: vueApp } = createVueApp('/')
  vueApp.mount('#app')
}
