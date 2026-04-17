import type { RegistrableApp } from 'qiankun'

// 生产环境：子应用与主壳同源部署，使用相对路径入口
// 开发环境：子应用分别在 3001 / 3002 端口独立运行
const isProd = import.meta.env.PROD

export const microApps: RegistrableApp<Record<string, unknown>>[] = [
  {
    name: 'blog-admin',
    entry: isProd ? '/blog-admin/' : '//localhost:3001',
    container: '#micro-container',
    activeRule: '/admin/blog',
  },
  {
    name: 'drive',
    entry: isProd ? '/drive/' : '//localhost:3002',
    container: '#micro-container',
    activeRule: '/admin/drive',
  },
]
