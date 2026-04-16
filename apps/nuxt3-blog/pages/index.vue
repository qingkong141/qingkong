<script setup lang="ts">
const route = useRoute()
const router = useRouter()

const currentPage = computed(() => Number(route.query.page) || 1)
const pageSize = 10

const { data, pending } = await useAsyncData(
  `posts-page-${currentPage.value}`,
  () => {
    const { list } = usePostApi()
    return list({ page: currentPage.value, pageSize, status: 'published' })
  },
  { watch: [currentPage] },
)

const posts = computed(() => data.value?.items ?? [])
const totalPages = computed(() => Math.ceil((data.value?.total ?? 0) / pageSize))

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
    <section class="hero">
      <h1 class="hero-title">青空</h1>
      <p class="hero-desc">记录技术与生活的点滴</p>
    </section>

    <!-- Loading -->
    <div v-if="pending" class="loading-wrap">
      <div class="loading-dots">
        <span /><span /><span />
      </div>
    </div>

    <!-- Posts -->
    <div v-else-if="posts.length" class="post-list">
      <article v-for="post in posts" :key="post.id" class="post-card">
        <NuxtLink :to="`/post/${post.slug}`" class="post-cover-link">
          <div class="post-cover">
            <img v-if="post.coverImage" :src="post.coverImage" :alt="post.title" />
            <div v-else class="post-cover-placeholder">
              <span>◈</span>
            </div>
          </div>
        </NuxtLink>

        <div class="post-body">
          <div class="post-meta">
            <time>{{ formatDate(post.createdAt) }}</time>
            <NuxtLink v-if="post.category" :to="`/categories/${post.category.slug}`" class="post-category">
              {{ post.category.name }}
            </NuxtLink>
          </div>

          <h2 class="post-title">
            <NuxtLink :to="`/post/${post.slug}`">{{ post.title }}</NuxtLink>
          </h2>

          <p v-if="post.summary" class="post-excerpt">{{ post.summary }}</p>

          <div v-if="post.tags.length" class="post-tags">
            <NuxtLink
              v-for="tag in post.tags"
              :key="tag.id"
              :to="`/tags/${tag.slug}`"
              class="tag"
              :style="tag.color ? { background: tag.color + '18', color: tag.color } : {}"
            >
              {{ tag.name }}
            </NuxtLink>
          </div>
        </div>
      </article>
    </div>

    <!-- Empty -->
    <div v-else class="empty">
      <div class="empty-icon">✦</div>
      <p>还没有文章，敬请期待</p>
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1" class="pagination">
      <button :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">← 上一页</button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">下一页 →</button>
    </nav>
  </div>
</template>

<style scoped>
/* ── Hero ─────────────── */
.hero {
  text-align: center;
  padding: 40px 0 48px;
}

.hero-title {
  font-size: 40px;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, var(--color-accent), #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  margin-top: 8px;
  font-size: 16px;
  color: var(--color-text-3);
}

/* ── Loading ──────────── */
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.loading-dots {
  display: flex;
  gap: 6px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
  animation: pulse 1.2s infinite ease-in-out;
}

.loading-dots span:nth-child(2) { animation-delay: 0.15s; }
.loading-dots span:nth-child(3) { animation-delay: 0.3s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* ── Post list ────────── */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.post-card {
  display: flex;
  gap: 24px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, transform 0.2s;
}

.post-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.post-cover-link {
  flex-shrink: 0;
  width: 280px;
}

.post-cover {
  width: 100%;
  height: 100%;
  min-height: 200px;
  overflow: hidden;
}

.post-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.post-card:hover .post-cover img {
  transform: scale(1.03);
}

.post-cover-placeholder {
  width: 100%;
  height: 100%;
  min-height: 200px;
  background: linear-gradient(135deg, #e0e7ff, #f0f0ff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: var(--color-accent);
  opacity: 0.5;
}

.post-body {
  flex: 1;
  padding: 24px 24px 24px 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-3);
  margin-bottom: 8px;
}

.post-category {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-accent-light);
  color: var(--color-accent);
  font-weight: 500;
  font-size: 12px;
  transition: background 0.15s;
}

.post-category:hover {
  background: rgba(99, 102, 241, 0.15);
}

.post-title {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 8px;
}

.post-title a {
  transition: color 0.15s;
}

.post-title a:hover {
  color: var(--color-accent);
}

.post-excerpt {
  font-size: 14px;
  color: var(--color-text-2);
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 12px;
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: auto;
}

.tag {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: var(--color-tag-bg);
  color: var(--color-tag-text);
  transition: opacity 0.15s;
}

.tag:hover { opacity: 0.8; }

/* ── Empty ────────────── */
.empty {
  text-align: center;
  padding: 80px 0;
  color: var(--color-text-3);
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
  opacity: 0.4;
}

/* ── Pagination ───────── */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 48px;
  padding: 24px 0;
}

.pagination button {
  padding: 8px 18px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-2);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.pagination button:hover:not(:disabled) {
  color: var(--color-accent);
  border-color: var(--color-accent);
  background: var(--color-accent-light);
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: var(--color-text-3);
  font-weight: 500;
}

/* ── Responsive ───────── */
@media (max-width: 768px) {
  .hero { padding: 24px 0 32px; }
  .hero-title { font-size: 28px; }

  .post-card {
    flex-direction: column;
  }

  .post-cover-link {
    width: 100%;
  }

  .post-cover,
  .post-cover-placeholder {
    min-height: 160px;
    max-height: 200px;
  }

  .post-body {
    padding: 16px;
  }

  .post-title { font-size: 17px; }
}
</style>
