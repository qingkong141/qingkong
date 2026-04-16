<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import { setupMicroApps } from '../micro'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const collapsed = ref(localStorage.getItem('sidebar') === 'collapsed')

function toggleSidebar() {
  collapsed.value = !collapsed.value
  localStorage.setItem('sidebar', collapsed.value ? 'collapsed' : 'expanded')
}

onMounted(async () => {
  authStore.fetchUser()
  setupMicroApps()
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

interface MenuItem {
  name: string
  label: string
  path: string
  icon: string
  children?: { label: string; path: string }[]
}

const menuItems: MenuItem[] = [
  {
    name: 'blog-admin',
    label: '博客管理',
    path: '/admin/blog',
    icon: '✦',
    children: [
      { label: '文章管理', path: '/admin/blog/posts' },
      { label: '分类管理', path: '/admin/blog/categories' },
      { label: '标签管理', path: '/admin/blog/tags' },
    ],
  },
  {
    name: 'drive',
    label: '云盘',
    path: '/admin/drive',
    icon: '◈',
  },
]

const expandedMenus = ref<Set<string>>(new Set(['blog-admin']))

function toggleMenu(name: string) {
  if (expandedMenus.value.has(name)) expandedMenus.value.delete(name)
  else expandedMenus.value.add(name)
}

function isChildActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}

function isGroupActive(item: MenuItem) {
  if (!item.children) return route.path.startsWith(item.path)
  return item.children.some(c => isChildActive(c.path))
}
</script>

<template>
  <div class="shell">

    <!-- 左：侧边栏（全高） -->
    <aside class="sidebar" :class="{ collapsed }">

      <!-- logo 区域，与右侧顶栏等高 -->
      <div class="sidebar-header">
        <div class="brand-icon">Q</div>
        <span v-if="!collapsed" class="brand-name">青空管理台</span>
      </div>

      <!-- 菜单 -->
      <nav class="sidebar-nav">
        <p v-if="!collapsed" class="nav-label">功能模块</p>
        <div v-for="item in menuItems" :key="item.name" class="menu-group">
          <!-- 有子菜单：点击展开/收起 -->
          <div
            v-if="item.children"
            class="menu-item"
            :class="{ active: isGroupActive(item) && collapsed }"
            :title="collapsed ? item.label : ''"
            @click="collapsed ? router.push(item.children[0].path) : toggleMenu(item.name)"
          >
            <span class="menu-icon">{{ item.icon }}</span>
            <span v-if="!collapsed" class="menu-label">{{ item.label }}</span>
            <svg v-if="!collapsed" class="menu-arrow" :class="{ expanded: expandedMenus.has(item.name) }" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
          <!-- 子菜单项 -->
          <div v-if="item.children && !collapsed && expandedMenus.has(item.name)" class="sub-menu">
            <router-link
              v-for="child in item.children"
              :key="child.path"
              :to="child.path"
              class="sub-item"
              :class="{ active: isChildActive(child.path) }"
            >
              <span class="sub-dot"/>
              {{ child.label }}
            </router-link>
          </div>
          <!-- 无子菜单：直接导航 -->
          <router-link
            v-if="!item.children"
            :to="item.path"
            class="menu-item"
            :class="{ active: isGroupActive(item) }"
            :title="collapsed ? item.label : ''"
          >
            <span class="menu-icon">{{ item.icon }}</span>
            <span v-if="!collapsed" class="menu-label">{{ item.label }}</span>
          </router-link>
        </div>
      </nav>
    </aside>

    <!-- 右：顶栏 + 内容（纵向排列） -->
    <div class="main">

      <!-- 顶栏（只占右侧宽度） -->
      <header class="topbar">
        <div class="topbar-left">
          <button class="collapse-btn" :title="collapsed ? '展开菜单' : '收起菜单'" @click="toggleSidebar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="topbar-right">
          <!-- 主题切换 -->
          <button class="icon-btn" :title="themeStore.isDark ? '切换到浅色' : '切换到深色'" @click="themeStore.toggle()">
            <svg v-if="themeStore.isDark" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="5"/>
              <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
              <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>

          <span class="divider" />

          <!-- 用户头像 + 用户名，悬浮展开下拉菜单 -->
          <div class="user-dropdown">
            <div class="user-area">
              <div class="user-avatar">
                <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" class="avatar-img" />
                <span v-else class="avatar-letter">
                  {{ authStore.user?.username?.charAt(0).toUpperCase() }}
                </span>
              </div>
              <span class="username">{{ authStore.user?.username }}</span>
              <svg class="chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </div>

            <div class="dropdown-menu">
              <div class="dropdown-menu-inner">
                <div class="dropdown-header">
                  <span class="d-name">{{ authStore.user?.username }}</span>
                  <span class="d-email">{{ authStore.user?.email }}</span>
                </div>
                <div class="dropdown-divider" />
                <button class="dropdown-item danger" @click="handleLogout">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                    <polyline points="16 17 21 12 16 7"/>
                    <line x1="21" y1="12" x2="9" y2="12"/>
                  </svg>
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="content">
        <router-view />
        <div id="micro-container" />
      </main>

    </div>
  </div>
</template>

<style scoped>
.shell {
  height: 100vh;
  display: flex;
  flex-direction: row;   /* 左右排列：侧边栏 | 右侧主区 */
  background: var(--bg-page);
}

/* 右侧主区：顶栏 + 内容，纵向排列 */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* ── 顶栏 ── */
.topbar {
  height: 56px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px 0 12px;
  flex-shrink: 0;
  transition: background 0.3s, border-color 0.3s;
  z-index: 10;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 折叠按钮 */
.collapse-btn {
  background: none;
  border: none;
  color: var(--text-2);
  cursor: pointer;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
  flex-shrink: 0;
}
.collapse-btn:hover {
  background: var(--bg-hover);
  color: var(--text-1);
}

/* 侧边栏顶部 logo 区域 */
.sidebar-header {
  height: 56px;              /* 与顶栏等高，视觉对齐 */
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  overflow: hidden;
  transition: padding 0.25s ease;
}

/* 折叠时图标居中 */
.sidebar.collapsed .sidebar-header {
  padding: 0;
  justify-content: center;
}

.brand-icon {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, var(--accent), var(--accent-end));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.brand-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-1);
  white-space: nowrap;
  overflow: hidden;
}

/* 通用图标按钮 */
.icon-btn {
  background: none;
  border: 1px solid var(--border);
  color: var(--text-2);
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.icon-btn:hover {
  background: var(--bg-hover);
  color: var(--accent);
  border-color: var(--accent);
}

.divider {
  width: 1px;
  height: 18px;
  background: var(--border);
}

/* 用户下拉区域 */
.user-dropdown {
  position: relative;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 7px;
  height: 34px;
  padding: 0 10px 0 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  border: 1px solid transparent;
}

.user-dropdown:hover .user-area {
  background: var(--bg-hover);
  border-color: var(--border);
}

.avatar-img {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  object-fit: cover;
}

.avatar-letter {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: linear-gradient(135deg, var(--accent), var(--accent-end));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.username {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-1);
}

.chevron {
  color: var(--text-3);
  transition: transform 0.2s;
}

.user-dropdown:hover .chevron {
  transform: rotate(180deg);
}

/* 下拉菜单 */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 200px;
  /* padding-top 填充触发区和菜单之间的视觉间距，让鼠标经过时不会中断 hover */
  padding-top: 6px;
  opacity: 0;
  pointer-events: none;
  transform: translateY(-4px);
  transition: opacity 0.15s, transform 0.15s;
  z-index: 100;
}

.dropdown-menu-inner {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow-card);
  padding: 6px;
}

.user-dropdown:hover .dropdown-menu {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0);
}

.dropdown-header {
  padding: 8px 10px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.d-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-1);
}

.d-email {
  font-size: 12px;
  color: var(--text-3);
}

.dropdown-divider {
  height: 1px;
  background: var(--border);
  margin: 2px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  background: none;
  border: none;
  border-radius: 7px;
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s, color 0.15s;
  color: var(--text-2);
}

.dropdown-item:hover {
  background: var(--bg-hover);
}

.dropdown-item.danger:hover {
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
}

/* ── 侧边栏 ── */
.sidebar {
  width: 240px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease, background 0.3s, border-color 0.3s;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-nav {
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
}

/* 分组标题：只有展开时显示，左对齐和菜单文字对齐 */
.nav-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0 16px;
  margin: 10px 0 4px;
  white-space: nowrap;
}

/* 菜单项 */
.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 2px 8px;
  padding: 10px 12px;
  border-radius: 6px;
  color: var(--text-nav);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
  overflow: hidden;
  cursor: pointer;
}

.menu-item:hover {
  background: var(--bg-hover);
  color: var(--text-1);
}

.menu-item.active {
  background: var(--accent);
  color: #fff;
}

.menu-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.menu-label { flex: 1; }

.menu-arrow {
  color: var(--text-3);
  transition: transform 0.2s;
  flex-shrink: 0;
}
.menu-arrow.expanded { transform: rotate(90deg); }

/* 子菜单 */
.sub-menu {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 2px 0 4px;
}

.sub-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 8px;
  padding: 8px 12px 8px 22px;
  border-radius: 6px;
  color: var(--text-2);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
  overflow: hidden;
}

.sub-item:hover {
  background: var(--bg-hover);
  color: var(--text-1);
}

.sub-item.active {
  color: var(--accent);
  background: rgba(99, 102, 241, 0.08);
}

.sub-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--text-3);
  flex-shrink: 0;
  transition: background 0.15s;
}

.sub-item.active .sub-dot {
  background: var(--accent);
}

/* 折叠时 */
.sidebar.collapsed .menu-item {
  justify-content: center;
  margin: 2px 8px;
  padding: 10px 0;
  gap: 0;
}

.sidebar.collapsed .menu-icon {
  width: auto;
}

/* ── 内容区 ── */
.content {
  flex: 1;
  overflow: auto;
  padding: 10px;
  background: var(--bg-page);
  transition: background 0.3s;
}

#micro-container { min-height: 100%; }
</style>
