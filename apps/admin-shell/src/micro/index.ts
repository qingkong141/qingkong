import { registerMicroApps, start } from 'qiankun'
import { microApps } from './apps'

export function setupMicroApps() {
  registerMicroApps(microApps)
  start()
}
