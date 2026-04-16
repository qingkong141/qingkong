import { ref } from 'vue'

const visible = ref(false)
const title = ref('')
const message = ref('')
const confirmText = ref('确定')
const cancelText = ref('取消')
const isDanger = ref(false)

let _resolve: ((val: boolean) => void) | null = null

function open(opts: {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}): Promise<boolean> {
  title.value = opts.title || '提示'
  message.value = opts.message
  confirmText.value = opts.confirmText || '确定'
  cancelText.value = opts.cancelText || '取消'
  isDanger.value = opts.danger || false
  visible.value = true

  return new Promise((resolve) => {
    _resolve = resolve
  })
}

function confirm() {
  visible.value = false
  _resolve?.(true)
  _resolve = null
}

function cancel() {
  visible.value = false
  _resolve?.(false)
  _resolve = null
}

export function useConfirm() {
  return { visible, title, message, confirmText, cancelText, isDanger, open, confirm, cancel }
}
