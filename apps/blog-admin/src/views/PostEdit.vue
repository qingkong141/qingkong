<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { postApi, categoryApi, tagApi } from '@qingkong/shared-api'
import type { Category, Tag } from '@qingkong/shared-types'
import { showToast } from '../composables/toast'

const route = useRoute()
const router = useRouter()

// 跟随 shell 的 data-theme 属性切换编辑器主题
const editorTheme = ref<'light' | 'dark'>(
  document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light',
)
let themeObserver: MutationObserver | null = null
onMounted(() => {
  themeObserver = new MutationObserver(() => {
    editorTheme.value =
      document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
  })
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
})
onUnmounted(() => { themeObserver?.disconnect() })

const postId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})

const form = ref({
  title: '',
  content: '',
  summary: '',
  coverImage: '',
  categoryId: undefined as number | undefined,
  tagIds: [] as number[],
  status: 'draft' as 'draft' | 'published' | 'archived',
})

const categories = ref<{ id: number; label: string }[]>([])
const tags = ref<Tag[]>([])
const saving = ref(false)
const pageTitle = computed(() => postId.value ? '编辑文章' : '新建文章')

function flattenTree(cats: Category[], depth = 0): { id: number; label: string }[] {
  const result: { id: number; label: string }[] = []
  for (const c of cats) {
    result.push({ id: c.id, label: Array(depth * 2 + 1).join('\u00a0') + c.name })
    for (const child of flattenTree(c.children ?? [], depth + 1)) {
      result.push(child)
    }
  }
  return result
}

onMounted(async () => {
  const [catTree, tagList] = await Promise.all([categoryApi.list(), tagApi.list()])
  categories.value = flattenTree(catTree)
  tags.value = tagList

  if (postId.value) {
    const post = await postApi.get(postId.value)
    form.value = {
      title: post.title,
      content: post.content ?? '',
      summary: post.summary ?? '',
      coverImage: post.coverImage ?? '',
      categoryId: post.category?.id,
      tagIds: post.tags?.map(t => t.id) ?? [],
      status: post.status,
    }
  }
})

async function save(publishNow = false) {
  if (!form.value.title.trim()) { showToast('请输入文章标题', 'error'); return }
  if (publishNow) form.value.status = 'published'
  saving.value = true
  try {
    const payload = {
      title: form.value.title,
      content: form.value.content || undefined,
      summary: form.value.summary || undefined,
      coverImage: form.value.coverImage || undefined,
      categoryId: form.value.categoryId,
      tagIds: form.value.tagIds,
      status: form.value.status,
    }
    if (postId.value) await postApi.update(postId.value, payload)
    else await postApi.create(payload)
    router.push('/posts')
  } finally {
    saving.value = false
  }
}

function toggleTag(id: number) {
  const idx = form.value.tagIds.indexOf(id)
  if (idx === -1) form.value.tagIds.push(id)
  else form.value.tagIds.splice(idx, 1)
}
</script>

<template>
  <div class="edit-page">

    <!-- 顶栏 -->
    <header class="edit-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/posts')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          返回列表
        </button>
        <span class="header-divider"/>
        <h1 class="header-title">{{ pageTitle }}</h1>
      </div>
      <div class="header-right">
        <select v-model="form.status" class="status-select">
          <option value="draft">草稿</option>
          <option value="published">已发布</option>
          <option value="archived">已归档</option>
        </select>
        <button class="btn btn-ghost" :disabled="saving" @click="save(false)">
          {{ saving ? '保存中…' : '保存草稿' }}
        </button>
        <button class="btn btn-primary" :disabled="saving" @click="save(true)">发布</button>
      </div>
    </header>

    <!-- 主体 -->
    <div class="edit-body">

      <!-- 左：编辑区 -->
      <div class="edit-main">
        <input
          v-model="form.title"
          class="title-input"
          placeholder="请输入文章标题…"
        />
        <div class="editor-wrap">
          <MdEditor
            v-model="form.content"
            :preview="false"
            :theme="editorTheme"
            placeholder="开始写作…"
            style="height: 100%; border-radius: 8px; overflow: hidden;"
          />
        </div>
      </div>

      <!-- 右：配置栏 -->
      <aside class="edit-sidebar">

        <div class="s-card">
          <div class="s-card-label">分类</div>
          <select v-model="form.categoryId" class="s-select">
            <option :value="undefined">— 不选 —</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.label }}</option>
          </select>
        </div>

        <div class="s-card">
          <div class="s-card-label">标签</div>
          <div v-if="tags.length === 0" class="s-empty">暂无标签</div>
          <div v-else class="tag-wrap">
            <span
              v-for="tag in tags"
              :key="tag.id"
              class="tag-chip"
              :class="{ active: form.tagIds.includes(tag.id) }"
              @click="toggleTag(tag.id)"
            >
              <span v-if="tag.color" class="tag-dot" :style="{ background: tag.color }"/>
              {{ tag.name }}
            </span>
          </div>
        </div>

        <div class="s-card">
          <div class="s-card-label">摘要</div>
          <textarea
            v-model="form.summary"
            class="s-textarea"
            placeholder="可选，不填则自动截取正文…"
            rows="3"
          />
        </div>

        <div class="s-card">
          <div class="s-card-label">封面图 URL</div>
          <input v-model="form.coverImage" class="s-input" placeholder="https://…（选填）"/>
          <img v-if="form.coverImage" :src="form.coverImage" class="cover-preview" alt="封面预览"/>
        </div>

      </aside>
    </div>
  </div>
</template>

<style scoped>
.edit-page {
  display: flex;
  flex-direction: column;
  /* 56px 顶栏 + 10px*2 shell 内边距 */
  min-height: calc(100vh - 76px);
  background: var(--bg-surface, #fff);
  border-radius: 12px;
  overflow: hidden;
}

/* ── 顶栏 ── */
.edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 52px;
  background: var(--bg-surface, #fff);
  border-bottom: 1px solid var(--border, #e5e7eb);
  flex-shrink: 0;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  font-size: 13px;
  color: var(--text-2, #6b7280);
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  white-space: nowrap;
  transition: color 0.15s, background 0.15s;
}
.back-btn:hover { color: var(--accent, #6366f1); background: var(--bg-hover, #f3f4f6); }

.header-divider {
  width: 1px;
  height: 16px;
  background: var(--border, #e5e7eb);
  flex-shrink: 0;
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-1, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.status-select {
  height: 32px;
  padding: 0 28px 0 10px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 7px;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
  font-size: 13px;
  cursor: pointer;
  outline: none;
  appearance: auto;
}

.btn {
  height: 32px;
  padding: 0 14px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border, #e5e7eb);
  transition: all 0.15s;
  white-space: nowrap;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-ghost {
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
}
.btn-ghost:hover:not(:disabled) { background: var(--bg-hover, #f3f4f6); }

.btn-primary {
  background: var(--accent, #6366f1);
  color: #fff;
  border-color: var(--accent, #6366f1);
}
.btn-primary:hover:not(:disabled) { opacity: 0.88; }

/* ── 主体布局 ── */
.edit-body {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 0;
  background: var(--bg-surface, #fff);
}

/* 左侧 */
.edit-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 16px;
  gap: 10px;
}

.title-input {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 8px;
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 17px;
  font-weight: 600;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
  flex-shrink: 0;
}
.title-input:focus {
  border-color: var(--accent, #6366f1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}
.title-input::placeholder { color: var(--text-3, #9ca3af); font-weight: 400; font-size: 15px; }

.editor-wrap {
  flex: 1;
  min-height: 0;
  border-radius: 8px 0 0 8px;
  overflow: hidden;
  border-right: none;
}

/* 右侧配置栏 */
.edit-sidebar {
  width: 232px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  overflow-y: auto;
  background: var(--bg-surface, #fff);
  border-left: 1px solid var(--border, #e5e7eb);
}

/* ── 侧边卡片 ── */
.s-card {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.s-card-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-3, #9ca3af);
  text-transform: uppercase;
  letter-spacing: 0.07em;
}

.s-select {
  width: 100%;
  height: 30px;
  padding: 0 6px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 6px;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
  font-size: 13px;
  outline: none;
  cursor: pointer;
  box-sizing: border-box;
}

.s-input {
  width: 100%;
  height: 30px;
  padding: 0 8px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 6px;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
  font-size: 12px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s;
}
.s-input:focus { border-color: var(--accent, #6366f1); }

.s-textarea {
  width: 100%;
  padding: 7px 8px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 6px;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
  font-size: 12px;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  line-height: 1.5;
  transition: border-color 0.15s;
}
.s-textarea:focus { border-color: var(--accent, #6366f1); }

.s-empty { font-size: 12px; color: var(--text-3, #9ca3af); }

/* 标签 */
.tag-wrap { display: flex; flex-wrap: wrap; gap: 5px; }

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-2, #6b7280);
  cursor: pointer;
  user-select: none;
  transition: all 0.12s;
  background: var(--bg-page, #f5f5f7);
}
.tag-chip:hover { border-color: var(--accent, #6366f1); color: var(--accent, #6366f1); }
.tag-chip.active {
  background: var(--accent, #6366f1);
  border-color: var(--accent, #6366f1);
  color: #fff;
}

.tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 封面预览 */
.cover-preview {
  width: 100%;
  border-radius: 6px;
  object-fit: cover;
  max-height: 100px;
  border: 1px solid var(--border, #e5e7eb);
}
</style>
