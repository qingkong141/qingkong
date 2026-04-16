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

renderWithQiankun({
  bootstrap() {},

  mount(props) {
    const { app: vueApp } = createVueApp('/admin/drive')
    const container = (props as { container?: HTMLElement }).container
    vueApp.mount(container ? container.querySelector('#app')! : '#app')
  },

  unmount() {
    app?.unmount()
  },

  update() {},
})

if (!qiankunWindow.__POWERED_BY_QIANKUN__) {
  const { app: vueApp } = createVueApp('/')
  vueApp.mount('#app')
}
