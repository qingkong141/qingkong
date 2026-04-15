import { registerMicroApps, start } from 'qiankun'
import { microApps } from './apps'

let started = false

export function setupMicroApps() {
  if (started) return
  started = true
  registerMicroApps(microApps)
  // Vite 子应用需要关闭 sandbox，否则 ESM 模块运行会异常
  start({ sandbox: false })
}
