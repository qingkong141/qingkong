import type { RegistrableApp } from 'qiankun'

export const microApps: RegistrableApp<Record<string, unknown>>[] = [
  {
    name: 'blog-admin',
    entry: '//localhost:3001',
    container: '#micro-container',
    activeRule: '/admin/blog',
  },
  {
    name: 'drive',
    entry: '//127.0.0.1:3002',
    container: '#micro-container',
    activeRule: '/admin/drive',
  },
]
