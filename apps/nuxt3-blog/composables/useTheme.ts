type Theme = 'light' | 'dark'

const theme = ref<Theme>('light')

function applyTheme(t: Theme) {
  if (import.meta.server) return
  document.documentElement.classList.toggle('dark', t === 'dark')
}

export function useTheme() {
  function init() {
    if (import.meta.server) return
    const stored = localStorage.getItem('theme') as Theme | null
    if (stored) {
      theme.value = stored
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      theme.value = 'dark'
    }
    applyTheme(theme.value)
  }

  function toggle() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    applyTheme(theme.value)
  }

  return {
    theme: readonly(theme),
    init,
    toggle,
  }
}
