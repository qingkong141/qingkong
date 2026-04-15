import type { RegistrableApp } from 'qiankun'

export const microApps: RegistrableApp<Record<string, unknown>>[] = [
  {
    name: 'blog-admin',
    entry: '//127.0.0.1:8081',
    container: '#micro-container',
    activeRule: '/admin/blog',
  },
  {
    name: 'drive',
    entry: '//127.0.0.1:8082',
    container: '#micro-container',
    activeRule: '/admin/drive',
  },
]
