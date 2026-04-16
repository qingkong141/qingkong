<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fileApi } from '@qingkong/shared-api'
import type { StorageUsage } from '@qingkong/shared-api'

const usage = ref<StorageUsage | null>(null)

async function loadUsage() {
  try { usage.value = await fileApi.storageUsage() } catch {}
}

onMounted(loadUsage)
</script>

<template>
  <div class="page">
    <div v-if="usage" class="storage-strip">
      <span class="storage-label">存储</span>
      <div class="storage-track">
        <div class="storage-fill" :style="{ width: usage.percentage + '%' }" />
      </div>
      <span class="storage-text">{{ usage.usedFormatted }} / {{ usage.quotaFormatted }}</span>
    </div>
    <router-view />
  </div>
</template>

<style scoped>
.page {
  padding: 20px;
  min-height: calc(100vh - 76px);
  background: var(--bg-surface, #fff);
  border-radius: 12px;
  box-sizing: border-box;
}

.storage-strip {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border, #e5e7eb);
}

.storage-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-3, #9ca3af);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  white-space: nowrap;
}

.storage-track {
  flex: 1;
  max-width: 180px;
  height: 4px;
  background: var(--bg-page, #f9fafb);
  border-radius: 2px;
  overflow: hidden;
}

.storage-fill {
  height: 100%;
  background: var(--accent, #6366f1);
  border-radius: 2px;
  transition: width 0.3s;
}

.storage-text {
  font-size: 12px;
  color: var(--text-3, #9ca3af);
  white-space: nowrap;
}
</style>
