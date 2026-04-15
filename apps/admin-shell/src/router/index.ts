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
        // 微应用占位路由：让 Vue Router 认识 /admin/blog/* 和 /admin/drive/*
        // :any(.*)* 中的 * 让参数可选，同时匹配 /admin/blog 和 /admin/blog/posts 等
        // 不配置 component，<router-view> 渲染空内容，Layout 保持挂载
        // qiankun 通过 #micro-container 接管实际渲染
        { path: 'blog/:any(.*)*', component: { template: '' } },
        { path: 'drive/:any(.*)*', component: { template: '' } },
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
