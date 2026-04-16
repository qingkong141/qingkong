<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const slug = route.params.slug as string

const { data: category } = await useAsyncData(
  `category-${slug}`,
  () => useCategoryApi().getBySlug(slug),
)

if (!category.value) {
  throw createError({ statusCode: 404, message: '分类不存在' })
}

useHead({ title: `${category.value.name} - 青空` })

const currentPage = computed(() => Number(route.query.page) || 1)
const pageSize = 10

const { data: postsData, pending } = await useAsyncData(
  `category-posts-${slug}-${currentPage.value}`,
  () => usePostApi().list({ page: currentPage.value, pageSize, status: 'published', categoryId: category.value!.id }),
  { watch: [currentPage] },
)

const posts = computed(() => postsData.value?.items ?? [])
const totalPages = computed(() => Math.ceil((postsData.value?.total ?? 0) / pageSize))

function goPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  router.push({ query: { ...route.query, page: p } })
}

function formatDate(str: string) {
  const d = new Date(str)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <div class="container">
    <header class="page-header">
      <NuxtLink to="/categories" class="back-link">← 所有分类</NuxtLink>
      <h1 class="page-title">{{ category!.name }}</h1>
      <p v-if="category!.description" class="page-desc">{{ category!.description }}</p>
    </header>

    <div v-if="pending" class="loading">
      <span class="dot" /><span class="dot" /><span class="dot" />
    </div>

    <ul v-else-if="posts.length" class="post-list">
      <li v-for="post in posts" :key="post.id" class="post-item">
        <NuxtLink :to="`/post/${post.slug}`" class="post-link">
          <time class="post-date">{{ formatDate(post.createdAt) }}</time>
          <h2 class="post-title">{{ post.title }}</h2>
        </NuxtLink>
      </li>
    </ul>

    <div v-else class="empty">
      <p>该分类下暂无文章</p>
    </div>

    <nav v-if="totalPages > 1" class="pagination">
      <button :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">← 上一页</button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">下一页 →</button>
    </nav>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 32px; }

.back-link {
  font-size: 13px;
  color: var(--color-text-3);
  transition: color 0.15s;
}
.back-link:hover { color: var(--color-text-1); }

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-top: 8px;
}

.page-desc {
  font-size: 14px;
  color: var(--color-text-2);
  margin-top: 4px;
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

.post-list {
  display: flex;
  flex-direction: column;
}

.post-item {
  border-bottom: 1px solid var(--color-border-light, #f0f0f0);
}

.post-item:first-child {
  border-top: 1px solid var(--color-border-light, #f0f0f0);
}

.post-link {
  display: flex;
  align-items: baseline;
  gap: 16px;
  padding: 16px 0;
  transition: opacity 0.15s;
}

.post-link:hover { opacity: 0.6; }

.post-date {
  font-size: 13px;
  color: var(--color-text-3);
  flex-shrink: 0;
  width: 120px;
}

.post-title {
  font-size: 16px;
  font-weight: 500;
  line-height: 1.5;
}

.empty {
  text-align: center;
  padding: 80px 0;
  font-size: 14px;
  color: var(--color-text-3);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 40px;
}

.pagination button {
  padding: 8px 18px;
  border-radius: var(--radius-md, 10px);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-2);
  background: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  transition: color 0.15s, border-color 0.15s;
}

.pagination button:hover:not(:disabled) {
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: var(--color-text-3);
}
</style>
