<script setup lang="ts">
defineProps<{
  message?: string
}>()
</script>

<template>
  <div class="empty">
    <slot name="icon">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
    </slot>
    <div class="empty-text">
      <slot>{{ message ?? '暂无数据' }}</slot>
    </div>
  </div>
</template>

<style scoped>
.empty {
  text-align: center;
  padding: 48px 16px;
  color: var(--text-3, #9ca3af);
}
.empty svg { display: block; margin: 0 auto 10px; }
.empty-text { font-size: 13px; }
</style>
