<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  page: number
  totalPages: number
}>()

const emit = defineEmits<{
  'update:page': [value: number]
}>()

const visiblePages = computed(() => {
  const total = props.totalPages
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const current = props.page
  const pages: (number | '...')[] = [1]

  if (current > 3) pages.push('...')

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) pages.push(i)

  if (current < total - 2) pages.push('...')
  pages.push(total)

  return pages
})
</script>

<template>
  <div v-if="totalPages > 1" class="pagination">
    <span class="page-info">第 {{ page }} / {{ totalPages }} 页</span>
    <div class="page-btns">
      <button class="page-btn" :disabled="page <= 1" @click="emit('update:page', page - 1)">‹</button>
      <template v-for="(p, idx) in visiblePages" :key="idx">
        <span v-if="p === '...'" class="page-ellipsis">…</span>
        <button
          v-else
          class="page-btn"
          :class="{ active: p === page }"
          @click="emit('update:page', p)"
        >{{ p }}</button>
      </template>
      <button class="page-btn" :disabled="page >= totalPages" @click="emit('update:page', page + 1)">›</button>
    </div>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border, #e5e7eb);
  background: var(--bg-page, #f9fafb);
}

.page-info { font-size: 12px; color: var(--text-3, #9ca3af); }
.page-btns { display: flex; gap: 4px; align-items: center; }

.page-btn {
  min-width: 28px;
  height: 28px;
  padding: 0 6px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 6px;
  background: var(--bg-surface, #fff);
  color: var(--text-2, #6b7280);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.12s;
}
.page-btn:hover:not(:disabled) { border-color: var(--accent, #6366f1); color: var(--accent, #6366f1); }
.page-btn.active { background: var(--accent, #6366f1); border-color: var(--accent, #6366f1); color: #fff; }
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.page-ellipsis {
  font-size: 12px;
  color: var(--text-3, #9ca3af);
  padding: 0 2px;
}
</style>
