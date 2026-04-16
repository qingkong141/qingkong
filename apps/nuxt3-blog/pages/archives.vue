<script setup lang="ts">
import type { PostSummary } from '~/composables/useApi'

useHead({ title: '归档 - 青空' })

const { data, pending } = await useAsyncData(
  'archives',
  async () => {
    const { list } = usePostApi()
    const all: PostSummary[] = []
    let page = 1
    while (true) {
      const res = await list({ page, pageSize: 100, status: 'published' })
      all.push(...res.items)
      if (all.length >= res.total) break
      page++
    }
    return all
  },
)

interface YearGroup {
  year: number
  posts: PostSummary[]
}

const groups = computed<YearGroup[]>(() => {
  if (!data.value?.length) return []
  const map = new Map<number, PostSummary[]>()
  for (const post of data.value) {
    const year = new Date(post.createdAt).getFullYear()
    if (!map.has(year)) map.set(year, [])
    map.get(year)!.push(post)
  }
  return Array.from(map.entries())
    .sort((a, b) => b[0] - a[0])
    .map(([year, posts]) => ({ year, posts }))
})

function formatDate(str: string) {
  const d = new Date(str)
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${m}-${day}`
}
</script>

<template>
  <div class="container">
    <h1 class="page-title">归档</h1>
    <p v-if="data?.length" class="page-desc">共 {{ data.length }} 篇文章</p>

    <div v-if="pending" class="loading">
      <span class="dot" /><span class="dot" /><span class="dot" />
    </div>

    <div v-else-if="groups.length" class="archive-list">
      <section v-for="group in groups" :key="group.year" class="year-section">
        <h2 class="year-title">{{ group.year }}</h2>
        <ul class="year-posts">
          <li v-for="post in group.posts" :key="post.id" class="archive-item">
            <NuxtLink :to="`/post/${post.slug}`" class="archive-link">
              <time class="archive-date">{{ formatDate(post.createdAt) }}</time>
              <span class="archive-title">{{ post.title }}</span>
            </NuxtLink>
          </li>
        </ul>
      </section>
    </div>

    <div v-else class="empty">
      <p>暂无文章</p>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 700;
}

.page-desc {
  font-size: 14px;
  color: var(--color-text-3);
  margin-top: 4px;
  margin-bottom: 40px;
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

.archive-list {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.year-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-1);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--color-accent);
  display: inline-block;
}

.year-posts {
  display: flex;
  flex-direction: column;
}

.archive-item {
  border-bottom: 1px solid var(--color-border-light, #f0f0f0);
}

.archive-link {
  display: flex;
  align-items: baseline;
  gap: 16px;
  padding: 12px 0;
  transition: opacity 0.15s;
}

.archive-link:hover { opacity: 0.6; }

.archive-date {
  font-size: 13px;
  color: var(--color-text-3);
  flex-shrink: 0;
  width: 50px;
  font-variant-numeric: tabular-nums;
}

.archive-title {
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
}

.empty {
  text-align: center;
  padding: 80px 0;
  font-size: 14px;
  color: var(--color-text-3);
}
</style>
