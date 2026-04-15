import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      component: () => import('../views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/admin',
      component: () => import('../views/Layout.vue'),
      children: [
        {
          path: '',
          component: () => import('../views/Welcome.vue'),
        },
      ],
    },
    {
      path: '/',
      redirect: '/admin',
    },
  ],
})

// 路由守卫：未登录跳转到登录页
router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  if (!to.meta.public && !token) {
    return '/login'
  }
  // 已登录访问登录页，直接跳后台
  if (to.path === '/login' && token) {
    return '/admin'
  }
})

export default router
