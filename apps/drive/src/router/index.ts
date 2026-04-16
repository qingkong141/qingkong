import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../views/DriveLayout.vue'),
    children: [
      {
        path: '',
        name: 'files',
        component: () => import('../views/FileList.vue'),
      },
      {
        path: 'trash',
        name: 'trash',
        component: () => import('../views/TrashList.vue'),
      },
      {
        path: 'shares',
        name: 'shares',
        component: () => import('../views/ShareList.vue'),
      },
    ],
  },
]
