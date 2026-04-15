import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    // /admin/blog → /admin/blog/posts 默认跳转
    path: '/',
    redirect: '/posts',
  },
  {
    path: '/posts',
    component: () => import('../views/PostList.vue'),
  },
  {
    path: '/posts/new',
    component: () => import('../views/PostEdit.vue'),
  },
  {
    path: '/posts/:id/edit',
    component: () => import('../views/PostEdit.vue'),
  },
]
