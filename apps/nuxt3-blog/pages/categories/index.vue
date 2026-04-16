<script setup lang="ts">
import type { CategoryNode } from '~/composables/useApi'

useHead({ title: '分类 - 青空' })

const { data: tree, pending } = await useAsyncData(
  'categories',
  () => useCategoryApi().list(),
)

function countPosts(node: CategoryNode): number {
  let n = node.postCount ?? 0
  if (node.children) {
    for (const child of node.children) n += countPosts(child)
  }
  return n
}
</script>

<template>
  <div class="container">
    <h1 class="page-title">分类</h1>

    <div v-if="pending" class="loading">
      <span class="dot" /><span class="dot" /><span class="dot" />
    </div>

    <div v-else-if="tree?.length" class="cat-grid">
      <NuxtLink
        v-for="cat in tree"
        :key="cat.id"
        :to="`/categories/${cat.slug}`"
        class="cat-card"
      >
        <h2 class="cat-name">{{ cat.name }}</h2>
        <p v-if="cat.description" class="cat-desc">{{ cat.description }}</p>
        <div v-if="cat.children?.length" class="cat-children">
          <span v-for="child in cat.children" :key="child.id" class="cat-child">{{ child.name }}</span>
        </div>
      </NuxtLink>
    </div>

    <div v-else class="empty">
      <p>暂无分类</p>
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
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
  animation: pulse 1.2s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.15s; }
.dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.cat-card {
  padding: 24px;
  background: var(--color-surface, #fff);
  border-radius: var(--radius-lg, 16px);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, transform 0.2s;
}

.cat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.cat-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
}

.cat-desc {
  font-size: 14px;
  color: var(--color-text-2);
  line-height: 1.6;
  margin-bottom: 12px;
}

.cat-children {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cat-child {
  padding: 2px 10px;
  font-size: 12px;
  border-radius: 20px;
  background: var(--color-accent-light, rgba(99,102,241,0.08));
  color: var(--color-accent);
  font-weight: 500;
}

.empty {
  text-align: center;
  padding: 80px 0;
  font-size: 14px;
  color: var(--color-text-3);
}
</style>
