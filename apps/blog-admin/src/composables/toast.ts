import { reactive } from 'vue'

export type ToastType = 'info' | 'success' | 'error'

export interface Toast {
  id: number
  message: string
  type: ToastType
}

let nextId = 0
export const toasts = reactive<Toast[]>([])

export function showToast(message: string, type: ToastType = 'info') {
  const id = nextId++
  toasts.push({ id, message, type })
  setTimeout(() => {
    const idx = toasts.findIndex(t => t.id === id)
    if (idx !== -1) toasts.splice(idx, 1)
  }, 3000)
}
