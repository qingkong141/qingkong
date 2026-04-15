<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { postApi, categoryApi } from '@qingkong/shared-api'
import type { Post, Category } from '@qingkong/shared-types'

const router = useRouter()

// ── 数据 ──────────────────────────────────────────────────────
const posts = ref<Post[]>([])
const total = ref(0)
const loading = ref(false)

// ── 筛选 / 分页 ───────────────────────────────────────────────
const page = ref(1)
const PAGE_SIZE = 10
const search = ref('')
const filterStatus = ref('')
const filterCategoryId = ref<number | ''>('')

// 分类平铺列表（树形结构拍平，用于下拉）
const categories = ref<{ id: number; label: string }[]>([])

function flattenTree(cats: Category[], depth = 0): { id: number; label: string }[] {
  return cats.flatMap(c => [
    { id: c.id, label: '\u00a0'.repeat(depth * 2) + c.name },
    ...flattenTree(c.children ?? [], depth + 1),
  ])
}

// ── 删除确认 ──────────────────────────────────────────────────
const deleteTarget = ref<Post | null>(null)
const deleting = ref(false)

// ── 计算 ──────────────────────────────────────────────────────
const totalPages = computed(() => Math.ceil(total.value / PAGE_SIZE))

// ── 方法 ──────────────────────────────────────────────────────
async function fetchPosts() {
  loading.value = true
  try {
    const res = await postApi.list({
      page: page.value,
      pageSize: PAGE_SIZE,
      search: search.value || undefined,
      status: filterStatus.value || undefined,
      categoryId: filterCategoryId.value || undefined,
    })
    posts.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  const tree = await categoryApi.list()
  categories.value = flattenTree(tree)
}

onMounted(() => {
  fetchPosts()
  fetchCategories()
})

// 筛选变化时重置到第 1 页
watch([filterStatus, filterCategoryId], () => {
  page.value = 1
  fetchPosts()
})
watch(page, fetchPosts)

let searchTimer: ReturnType<typeof setTimeout>
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchPosts()
  }, 400)
}

function gotoEdit(id?: number) {
  router.push(id ? `/posts/${id}/edit` : '/posts/new')
}

function confirmDelete(post: Post) {
  deleteTarget.value = post
}

async function doDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await postApi.delete(deleteTarget.value.id)
    deleteTarget.value = null
    fetchPosts()
  } finally {
    deleting.value = false
  }
}

// ── 格式化 ────────────────────────────────────────────────────
const STATUS_LABEL: Record<string, string> = {
  draft: '草稿',
  published: '已发布',
  archived: '已归档',
}
const STATUS_CLASS: Record<string, string> = {
  draft: 'badge-draft',
  published: 'badge-published',
  archived: 'badge-archived',
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}
</script>

<template>
  <div class="page">
    <!-- 页面标题 + 新建按钮 -->
    <div class="page-header">
      <h2 class="page-title">文章列表</h2>
      <button class="btn btn-primary" @click="gotoEdit()">+ 新建文章</button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <input
        v-model="search"
        class="input filter-search"
        placeholder="搜索标题或内容…"
        @input="onSearchInput"
      />
      <select v-model="filterCategoryId" class="input filter-select">
        <option value="">全部分类</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.label }}</option>
      </select>
      <select v-model="filterStatus" class="input filter-select">
        <option value="">全部状态</option>
        <option value="draft">草稿</option>
        <option value="published">已发布</option>
        <option value="archived">已归档</option>
      </select>
    </div>

    <!-- 表格 -->
    <div class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>标题</th>
            <th>分类</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="td-center">加载中…</td>
          </tr>
          <tr v-else-if="posts.length === 0">
            <td colspan="5" class="td-center">暂无文章</td>
          </tr>
          <tr v-for="post in posts" :key="post.id">
            <td class="td-title">{{ post.title }}</td>
            <td>{{ post.category?.name ?? '—' }}</td>
            <td>
              <span class="badge" :class="STATUS_CLASS[post.status]">
                {{ STATUS_LABEL[post.status] ?? post.status }}
              </span>
            </td>
            <td>{{ formatDate(post.createdAt) }}</td>
            <td class="td-actions">
              <button class="btn-link" @click="gotoEdit(post.id)">编辑</button>
              <button class="btn-link danger" @click="confirmDelete(post)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <span class="page-info">共 {{ total }} 篇</span>
      <button class="page-btn" :disabled="page <= 1" @click="page--">‹</button>
      <button
        v-for="p in totalPages"
        :key="p"
        class="page-btn"
        :class="{ active: p === page }"
        @click="page = p"
      >{{ p }}</button>
      <button class="page-btn" :disabled="page >= totalPages" @click="page++">›</button>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="deleteTarget" class="modal-mask">
      <div class="modal">
        <p class="modal-msg">确定删除「{{ deleteTarget.title }}」？此操作不可撤销。</p>
        <div class="modal-actions">
          <button class="btn" @click="deleteTarget = null">取消</button>
          <button class="btn btn-danger" :disabled="deleting" @click="doDelete">
            {{ deleting ? '删除中…' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px;
  min-height: 100%;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-1, #111);
}

/* ── 筛选栏 ── */
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.input {
  height: 34px;
  padding: 0 10px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 7px;
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}

.input:focus {
  border-color: var(--accent, #6366f1);
}

.filter-search { width: 220px; }
.filter-select { min-width: 120px; cursor: pointer; }

/* ── 表格 ── */
.table-wrap {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 10px;
  overflow: hidden;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th {
  padding: 11px 14px;
  text-align: left;
  font-weight: 500;
  color: var(--text-2, #555);
  background: var(--bg-page, #f5f5f7);
  border-bottom: 1px solid var(--border, #e0e0e0);
  white-space: nowrap;
}

.table td {
  padding: 11px 14px;
  border-bottom: 1px solid var(--border, #e0e0e0);
  color: var(--text-1, #111);
  vertical-align: middle;
}

.table tr:last-child td { border-bottom: none; }
.table tbody tr:hover td { background: var(--bg-hover, #f0f0f4); }

.td-title {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.td-center { text-align: center; color: var(--text-3, #999); }

.td-actions { display: flex; gap: 10px; }

/* ── 状态徽章 ── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-draft     { background: #f0f0f4; color: #666; }
.badge-published { background: #ecfdf5; color: #059669; }
.badge-archived  { background: #fef3c7; color: #b45309; }

/* ── 按钮 ── */
.btn {
  height: 34px;
  padding: 0 14px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 7px;
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.btn:hover { background: var(--bg-hover, #f0f0f4); }

.btn-primary {
  background: var(--accent, #6366f1);
  color: #fff;
  border-color: var(--accent, #6366f1);
}

.btn-primary:hover { opacity: 0.9; }

.btn-danger {
  background: #ef4444;
  color: #fff;
  border-color: #ef4444;
}

.btn-danger:hover { opacity: 0.9; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-link {
  background: none;
  border: none;
  padding: 0;
  font-size: 13px;
  color: var(--accent, #6366f1);
  cursor: pointer;
}

.btn-link:hover { text-decoration: underline; }
.btn-link.danger { color: #ef4444; }

/* ── 分页 ── */
.pagination {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 16px;
  justify-content: flex-end;
}

.page-info { font-size: 13px; color: var(--text-3, #999); margin-right: 8px; }

.page-btn {
  min-width: 30px;
  height: 30px;
  padding: 0 6px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 6px;
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--accent, #6366f1);
  color: var(--accent, #6366f1);
}

.page-btn.active {
  background: var(--accent, #6366f1);
  border-color: var(--accent, #6366f1);
  color: #fff;
}

.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── 删除确认弹窗 ── */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 12px;
  padding: 24px;
  width: 360px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.modal-msg {
  font-size: 14px;
  color: var(--text-1, #111);
  margin-bottom: 20px;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
