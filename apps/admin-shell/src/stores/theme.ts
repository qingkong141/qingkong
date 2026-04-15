import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 默认浅色，读取 localStorage 里的上次偏好
  const isDark = ref(localStorage.getItem('theme') === 'dark')

  function toggle() {
    isDark.value = !isDark.value
  }

  // 每次 isDark 变化，同步写入 localStorage 并更新 html 的 data-theme 属性
  watch(
    isDark,
    (val) => {
      localStorage.setItem('theme', val ? 'dark' : 'light')
      document.documentElement.setAttribute('data-theme', val ? 'dark' : 'light')
    },
    { immediate: true }, // 页面刷新时立即执行一次，防止闪烁
  )

  return { isDark, toggle }
})
