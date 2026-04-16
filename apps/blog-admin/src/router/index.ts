import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
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
  {
    path: '/categories',
    component: () => import('../views/CategoryList.vue'),
  },
  {
    path: '/tags',
    component: () => import('../views/TagList.vue'),
  },
  {
    path: '/comments',
    component: () => import('../views/CommentList.vue'),
  },
]
