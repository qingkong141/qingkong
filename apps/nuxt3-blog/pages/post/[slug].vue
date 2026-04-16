<script setup lang="ts">
import 'highlight.js/styles/github.css'
import 'katex/dist/katex.min.css'

const route = useRoute()
const slug = route.params.slug as string

const { data: post } = await useAsyncData(
  `post-${slug}`,
  () => usePostApi().getBySlug(slug),
)

if (!post.value) {
  throw createError({ statusCode: 404, message: '文章不存在' })
}

useHead({
  title: post.value.title + ' - 青空',
})

const { html: renderedContent, toc } = useMarkdown(post.value.content || '')

function formatDate(str: string) {
  const d = new Date(str)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <div class="container">
    <ReadingProgress />

    <div class="article-layout" :class="{ 'has-toc': toc.length > 0 }">
      <article class="article">
        <header class="article-header">
          <div class="article-meta">
            <time>{{ formatDate(post!.createdAt) }}</time>
            <span v-if="post!.category" class="article-cat">
              <NuxtLink :to="`/categories/${post!.category.slug}`">{{ post!.category.name }}</NuxtLink>
            </span>
          </div>
          <h1 class="article-title">{{ post!.title }}</h1>
          <div v-if="post!.tags.length" class="article-tags">
            <NuxtLink
              v-for="tag in post!.tags"
              :key="tag.id"
              :to="`/tags/${tag.slug}`"
              class="tag"
              :style="tag.color ? { background: tag.color + '18', color: tag.color } : {}"
            >
              {{ tag.name }}
            </NuxtLink>
          </div>
        </header>

        <div v-if="post!.coverImage" class="article-cover">
          <img :src="post!.coverImage" :alt="post!.title" />
        </div>

        <div class="article-content" v-html="renderedContent" />

        <footer class="article-footer">
          <NuxtLink to="/" class="back-link">← 返回文章列表</NuxtLink>
        </footer>
      </article>

      <aside v-if="toc.length > 0" class="article-aside">
        <TableOfContents :items="toc" />
      </aside>
    </div>
  </div>
</template>

<style scoped>
.article-layout {
  max-width: 720px;
  margin: 0 auto;
}

.article-layout.has-toc {
  max-width: 1000px;
  display: flex;
  gap: 48px;
}

.article {
  flex: 1;
  min-width: 0;
  max-width: 720px;
}

.article-aside {
  width: 220px;
  flex-shrink: 0;
  display: none;
}

.article-layout.has-toc .article-aside {
  display: block;
}

.article-header {
  margin-bottom: 32px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-3);
  margin-bottom: 12px;
}

.article-cat a {
  color: var(--color-accent);
  font-weight: 500;
  transition: opacity 0.15s;
}

.article-cat a:hover {
  opacity: 0.7;
}

.article-title {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: -0.3px;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 16px;
}

.tag {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: var(--color-tag-bg, #f3f4f6);
  color: var(--color-tag-text, #6b7280);
  transition: opacity 0.15s;
}

.tag:hover { opacity: 0.8; }

.article-cover {
  margin-bottom: 32px;
  border-radius: var(--radius-lg, 16px);
  overflow: hidden;
}

.article-cover img {
  width: 100%;
}

/* ── Article content typography ── */
.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--color-text-1);
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3),
.article-content :deep(h4) {
  margin-top: 2em;
  margin-bottom: 0.6em;
  font-weight: 600;
  line-height: 1.4;
}

.article-content :deep(h2) { font-size: 22px; }
.article-content :deep(h3) { font-size: 18px; }

.article-content :deep(p) {
  margin-bottom: 1.2em;
}

.article-content :deep(a) {
  color: var(--color-accent);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.article-content :deep(img) {
  border-radius: var(--radius-md, 10px);
  margin: 1.5em 0;
}

.article-content :deep(blockquote) {
  border-left: 3px solid var(--color-border, #e5e7eb);
  padding-left: 16px;
  margin: 1.5em 0;
  color: var(--color-text-2);
  font-style: italic;
}

.article-content :deep(pre.hljs) {
  background: #f8f8fa;
  border-radius: var(--radius-md, 10px);
  padding: 16px 20px;
  overflow-x: auto;
  margin: 1.5em 0;
  font-size: 14px;
  line-height: 1.6;
}

.article-content :deep(code) {
  font-family: var(--font-mono, monospace);
  font-size: 0.9em;
}

.article-content :deep(p code),
.article-content :deep(li code) {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 1em 0;
  padding-left: 1.5em;
}

.article-content :deep(ul) { list-style: disc; }
.article-content :deep(ol) { list-style: decimal; }

.article-content :deep(li) {
  margin-bottom: 0.4em;
}

.article-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--color-border, #e5e7eb);
  margin: 2em 0;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
  font-size: 14px;
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid var(--color-border, #e5e7eb);
  padding: 8px 12px;
  text-align: left;
}

.article-content :deep(th) {
  background: #f8f8fa;
  font-weight: 600;
}

.article-footer {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--color-border, #e5e7eb);
}

.back-link {
  font-size: 14px;
  color: var(--color-text-3);
  transition: color 0.15s;
}

.back-link:hover {
  color: var(--color-text-1);
}

@media (max-width: 1080px) {
  .article-aside { display: none !important; }
  .article-layout.has-toc { max-width: 720px; display: block; }
}

@media (max-width: 768px) {
  .article-title { font-size: 22px; }
}
</style>
