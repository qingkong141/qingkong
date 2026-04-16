<script setup lang="ts">
useHead({ title: '标签 - 青空' })

const { data: tags, pending } = await useAsyncData(
  'tags',
  () => useTagApi().list(),
)
</script>

<template>
  <div class="container">
    <h1 class="page-title">标签</h1>

    <div v-if="pending" class="loading">
      <span class="dot" /><span class="dot" /><span class="dot" />
    </div>

    <div v-else-if="tags?.length" class="tag-cloud">
      <NuxtLink
        v-for="tag in tags"
        :key="tag.id"
        :to="`/tags/${tag.slug}`"
        class="tag-item"
        :style="tag.color ? { background: tag.color + '14', color: tag.color, borderColor: tag.color + '30' } : {}"
      >
        {{ tag.name }}
      </NuxtLink>
    </div>

    <div v-else class="empty">
      <p>暂无标签</p>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 32px;
}

.loading {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 80px 0;
}

.dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--color-accent);
  animation: pulse 1.2s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.15s; }
.dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-item {
  padding: 8px 18px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  background: var(--color-tag-bg, #f3f4f6);
  color: var(--color-tag-text, #6b7280);
  border: 1px solid transparent;
  transition: transform 0.15s, box-shadow 0.15s;
}

.tag-item:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.empty {
  text-align: center;
  padding: 80px 0;
  font-size: 14px;
  color: var(--color-text-3);
}
</style>
