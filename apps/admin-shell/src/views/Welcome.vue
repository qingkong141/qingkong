<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
</script>

<template>
  <div class="welcome">
    <div class="welcome-card">
      <div class="avatar-big">
        <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" class="avatar-img" />
        <span v-else class="avatar-letter">
          {{ authStore.user?.username?.charAt(0).toUpperCase() }}
        </span>
      </div>
      <h2>{{ authStore.user?.username ? `你好，${authStore.user.username}` : '欢迎回来' }}</h2>
      <p>从左侧菜单选择功能模块开始使用</p>
      <div class="quick-links">
        <router-link to="/admin/blog" class="quick-btn">
          <span class="ql-icon">✦</span>
          <span>博客管理</span>
        </router-link>
        <router-link to="/admin/drive" class="quick-btn">
          <span class="ql-icon">◈</span>
          <span>云盘</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.welcome {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.welcome-card {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.avatar-big { margin-bottom: 4px; }

.avatar-img {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  object-fit: cover;
}

.avatar-letter {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--accent), var(--accent-end));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 600;
}

h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-1);
}

p {
  margin: 0;
  font-size: 14px;
  color: var(--text-3);
}

.quick-links {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text-2);
  text-decoration: none;
  font-size: 14px;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.quick-btn:hover {
  border-color: var(--accent);
  color: var(--text-nav-act);
  background: var(--bg-active);
}

.ql-icon { font-size: 13px; }
</style>
