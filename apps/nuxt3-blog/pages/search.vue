<script setup lang="ts">
import type { PostSummary } from '~/composables/useApi'

useHead({ title: '搜索 - 青空' })

const route = useRoute()
const router = useRouter()

const keyword = ref((route.query.q as string) || '')
const searchResults = ref<PostSummary[]>([])
const total = ref(0)
const loading = ref(false)
const searched = ref(false)

let timer: ReturnType<typeof setTimeout> | null = null

function debounceSearch() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => doSearch(), 350)
}

async function doSearch() {
  const q = keyword.value.trim()
  if (!q) {
    searchResults.value = []
    total.value = 0
    searched.value = false
    return
  }

  router.replace({ query: { q } })
  loading.value = true
  searched.value = true

  try {
    const { list } = usePostApi()
    const res = await list({ search: q, pageSize: 50, status: 'published' })
    searchResults.value = res.items
    total.value = res.total
  } catch {
    searchResults.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function highlight(text: string) {
  const q = keyword.value.trim()
  if (!q || !text) return text
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(
    new RegExp(`(${escaped})`, 'gi'),
    '<mark>$1</mark>',
  )
}

function formatDate(str: string) {
  const d = new Date(str)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(() => {
  if (keyword.value) doSearch()
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">搜索</h1>

    <div class="search-box">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input
        v-model="keyword"
        type="text"
        placeholder="输入关键词搜索文章..."
        class="search-input"
        autofocus
        @input="debounceSearch"
        @keydown.enter="doSearch"
      />
      <button v-if="keyword" class="search-clear" @click="keyword = ''; doSearch()">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">
      <span class="dot" /><span class="dot" /><span class="dot" />
    </div>

    <!-- Results -->
    <div v-else-if="searchResults.length" class="results">
      <p class="results-count">找到 {{ total }} 篇相关文章</p>
      <ul class="result-list">
        <li v-for="post in searchResults" :key="post.id" class="result-item">
          <NuxtLink :to="`/post/${post.slug}`" class="result-link">
            <div class="result-meta">
              <time>{{ formatDate(post.createdAt) }}</time>
              <span v-if="post.category" class="result-cat">{{ post.category.name }}</span>
            </div>
            <h2 class="result-title" v-html="highlight(post.title)" />
            <p v-if="post.summary" class="result-summary" v-html="highlight(post.summary)" />
          </NuxtLink>
        </li>
      </ul>
    </div>

    <!-- Empty -->
    <div v-else-if="searched" class="empty">
      <p>没有找到与「{{ keyword }}」相关的文章</p>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 32px;
}

.search-icon {
  position: absolute;
  left: 14px;
  color: var(--color-text-3);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 42px;
  font-size: 15px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-1);
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.search-input::placeholder {
  color: var(--color-text-3);
}

.search-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-light);
}

.search-clear {
  position: absolute;
  right: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: var(--color-text-3);
  transition: color 0.15s, background 0.15s;
}

.search-clear:hover {
  color: var(--color-text-1);
  background: var(--color-accent-light);
}

.loading {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 60px 0;
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

.results-count {
  font-size: 14px;
  color: var(--color-text-3);
  margin-bottom: 16px;
}

.result-list {
  display: flex;
  flex-direction: column;
}

.result-item {
  border-bottom: 1px solid var(--color-border-light);
}

.result-item:first-child {
  border-top: 1px solid var(--color-border-light);
}

.result-link {
  display: block;
  padding: 20px 0;
  transition: opacity 0.15s;
}

.result-link:hover { opacity: 0.6; }

.result-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-3);
  margin-bottom: 4px;
}

.result-cat {
  color: var(--color-accent);
  font-weight: 500;
}

.result-title {
  font-size: 17px;
  font-weight: 600;
  line-height: 1.5;
}

.result-summary {
  margin-top: 4px;
  font-size: 14px;
  color: var(--color-text-2);
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-title :deep(mark),
.result-summary :deep(mark) {
  background: rgba(99, 102, 241, 0.15);
  color: var(--color-accent);
  padding: 1px 2px;
  border-radius: 2px;
}

.empty {
  text-align: center;
  padding: 60px 0;
  font-size: 14px;
  color: var(--color-text-3);
}
</style>
