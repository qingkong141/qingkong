<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { postApi, categoryApi, tagApi } from '@qingkong/shared-api'
import type { Category, Tag } from '@qingkong/shared-types'

const route = useRoute()
const router = useRouter()

// 编辑模式：路由带 :id 参数
const postId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})

// ── 表单数据 ──────────────────────────────────────────────────
const form = ref({
  title: '',
  content: '',
  summary: '',
  coverImage: '',
  categoryId: undefined as number | undefined,
  tagIds: [] as number[],
  status: 'draft' as 'draft' | 'published',
})

// ── 辅助数据 ──────────────────────────────────────────────────
const categories = ref<{ id: number; label: string }[]>([])
const tags = ref<Tag[]>([])

function flattenTree(cats: Category[], depth = 0): { id: number; label: string }[] {
  return cats.flatMap(c => [
    { id: c.id, label: '\u00a0'.repeat(depth * 2) + c.name },
    ...flattenTree(c.children ?? [], depth + 1),
  ])
}

// ── 状态 ──────────────────────────────────────────────────────
const saving = ref(false)
const pageTitle = computed(() => postId.value ? '编辑文章' : '新建文章')

// ── 初始化 ────────────────────────────────────────────────────
onMounted(async () => {
  const [catTree, tagList] = await Promise.all([
    categoryApi.list(),
    tagApi.list(),
  ])
  categories.value = flattenTree(catTree)
  tags.value = tagList

  // 编辑模式：拉取现有文章并填入表单
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

// ── 保存 ──────────────────────────────────────────────────────
async function save(publishNow = false) {
  if (!form.value.title.trim()) {
    alert('请输入标题')
    return
  }
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

    if (postId.value) {
      await postApi.update(postId.value, payload)
    } else {
      await postApi.create(payload)
    }
    router.push('/posts')
  } finally {
    saving.value = false
  }
}

// ── 标签多选辅助 ──────────────────────────────────────────────
function toggleTag(id: number) {
  const idx = form.value.tagIds.indexOf(id)
  if (idx === -1) form.value.tagIds.push(id)
  else form.value.tagIds.splice(idx, 1)
}
</script>

<template>
  <div class="page">
    <!-- 顶栏 -->
    <div class="page-header">
      <button class="btn-back" @click="router.push('/posts')">← 返回列表</button>
      <h2 class="page-title">{{ pageTitle }}</h2>
    </div>

    <!-- 主体：左侧编辑区 + 右侧配置栏 -->
    <div class="editor-layout">

      <!-- 左：标题 + Markdown 编辑器 -->
      <div class="editor-main">
        <input
          v-model="form.title"
          class="title-input"
          placeholder="请输入文章标题…"
        />
        <MdEditor
          v-model="form.content"
          class="md-editor"
          :preview="false"
          placeholder="开始写作…"
        />
      </div>

      <!-- 右：配置侧边栏 -->
      <aside class="editor-sidebar">

        <!-- 发布操作 -->
        <div class="sidebar-card">
          <div class="sidebar-card-title">发布</div>
          <div class="status-row">
            <label class="field-label">状态</label>
            <select v-model="form.status" class="input">
              <option value="draft">草稿</option>
              <option value="published">已发布</option>
              <option value="archived">已归档</option>
            </select>
          </div>
          <div class="btn-group">
            <button class="btn" :disabled="saving" @click="save(false)">
              {{ saving ? '保存中…' : '保存草稿' }}
            </button>
            <button class="btn btn-primary" :disabled="saving" @click="save(true)">
              发布
            </button>
          </div>
        </div>

        <!-- 分类 -->
        <div class="sidebar-card">
          <div class="sidebar-card-title">分类</div>
          <select v-model="form.categoryId" class="input full">
            <option :value="undefined">— 不选 —</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.label }}</option>
          </select>
        </div>

        <!-- 标签 -->
        <div class="sidebar-card">
          <div class="sidebar-card-title">标签</div>
          <div v-if="tags.length === 0" class="no-tags">暂无标签</div>
          <div class="tag-list">
            <label
              v-for="tag in tags"
              :key="tag.id"
              class="tag-item"
              :class="{ selected: form.tagIds.includes(tag.id) }"
              @click="toggleTag(tag.id)"
            >
              <span
                v-if="tag.color"
                class="tag-dot"
                :style="{ background: tag.color }"
              />
              {{ tag.name }}
            </label>
          </div>
        </div>

        <!-- 摘要 -->
        <div class="sidebar-card">
          <div class="sidebar-card-title">摘要</div>
          <textarea
            v-model="form.summary"
            class="textarea"
            placeholder="可选，不填则自动截取正文…"
            rows="3"
          />
        </div>

        <!-- 封面图 -->
        <div class="sidebar-card">
          <div class="sidebar-card-title">封面图 URL</div>
          <input v-model="form.coverImage" class="input full" placeholder="https://…（选填）" />
          <img
            v-if="form.coverImage"
            :src="form.coverImage"
            class="cover-preview"
            alt="封面预览"
          />
        </div>

      </aside>
    </div>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
}

/* ── 顶栏 ── */
.page-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 24px 12px;
  flex-shrink: 0;
}

.btn-back {
  background: none;
  border: none;
  font-size: 13px;
  color: var(--text-2, #555);
  cursor: pointer;
  padding: 0;
}
.btn-back:hover { color: var(--accent, #6366f1); }

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-1, #111);
}

/* ── 布局 ── */
.editor-layout {
  display: flex;
  flex: 1;
  gap: 16px;
  padding: 0 24px 24px;
  min-height: 0;
}

/* 左侧 */
.editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

.title-input {
  width: 100%;
  height: 46px;
  padding: 0 14px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 8px;
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 18px;
  font-weight: 600;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s;
}
.title-input:focus { border-color: var(--accent, #6366f1); }
.title-input::placeholder { color: var(--text-3, #aaa); font-weight: 400; }

/* md-editor 撑满剩余高度 */
.md-editor {
  flex: 1;
  min-height: 0;
}

/* 右侧配置栏 */
.editor-sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
}

/* ── 侧边卡片 ── */
.sidebar-card {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 10px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-card-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-3, #999);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* ── 通用表单元素 ── */
.input {
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 6px;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}
.input:focus { border-color: var(--accent, #6366f1); }
.input.full { width: 100%; }

.textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 6px;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
  font-size: 13px;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  transition: border-color 0.15s;
}
.textarea:focus { border-color: var(--accent, #6366f1); }

/* ── 状态行 ── */
.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.field-label {
  font-size: 13px;
  color: var(--text-2, #555);
  white-space: nowrap;
}
.status-row .input { flex: 1; }

/* ── 按钮组 ── */
.btn-group {
  display: flex;
  gap: 8px;
}

.btn {
  flex: 1;
  height: 32px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 7px;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}
.btn:hover:not(:disabled) { background: var(--bg-hover, #eaeaf4); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primary {
  background: var(--accent, #6366f1);
  border-color: var(--accent, #6366f1);
  color: #fff;
}
.btn-primary:hover:not(:disabled) { opacity: 0.9; }

/* ── 标签多选 ── */
.no-tags { font-size: 13px; color: var(--text-3, #aaa); }

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-2, #555);
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
  user-select: none;
}
.tag-item:hover { background: var(--bg-hover, #eaeaf4); }
.tag-item.selected {
  background: var(--accent, #6366f1);
  border-color: var(--accent, #6366f1);
  color: #fff;
}

.tag-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

/* ── 封面预览 ── */
.cover-preview {
  width: 100%;
  border-radius: 6px;
  object-fit: cover;
  max-height: 120px;
  border: 1px solid var(--border, #e0e0e0);
}
</style>
