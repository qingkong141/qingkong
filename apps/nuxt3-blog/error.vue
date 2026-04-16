<script setup lang="ts">
const props = defineProps<{ error: { statusCode: number; message?: string } }>()

const title = computed(() => {
  if (props.error.statusCode === 404) return '404'
  return String(props.error.statusCode)
})

const desc = computed(() => {
  if (props.error.statusCode === 404) return '页面不存在'
  return props.error.message || '出了点问题'
})

function handleBack() {
  clearError({ redirect: '/' })
}
</script>

<template>
  <div class="error-page">
    <p class="error-code">{{ title }}</p>
    <p class="error-desc">{{ desc }}</p>
    <button class="error-btn" @click="handleBack">返回首页</button>
  </div>
</template>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', 'Noto Sans SC', sans-serif;
  background: var(--color-bg);
}

.error-code {
  font-size: 72px;
  font-weight: 700;
  color: var(--color-border);
  line-height: 1;
}

.error-desc {
  margin-top: 12px;
  font-size: 15px;
  color: var(--color-text-3);
}

.error-btn {
  margin-top: 32px;
  padding: 8px 24px;
  font-size: 14px;
  color: var(--color-text-2);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: none;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}

.error-btn:hover {
  color: var(--color-text-1);
  border-color: var(--color-text-1);
}
</style>
