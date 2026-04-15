<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { postApi, categoryApi } from '@qingkong/shared-api'
import type { Post, Category } from '@qingkong/shared-types'

const router = useRouter()

const posts = ref<Post[]>([])
const total = ref(0)
const loading = ref(false)

const page = ref(1)
const PAGE_SIZE = 10
const search = ref('')
const filterStatus = ref('')
const filterCategoryId = ref<number | ''>('')

const categories = ref<{ id: number; label: string }[]>([])
const deleteTarget = ref<Post | null>(null)
const deleting = ref(false)

const totalPages = computed(() => Math.ceil(total.value / PAGE_SIZE))

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

onMounted(() => { fetchPosts(); fetchCategories() })

watch([filterStatus, filterCategoryId], () => { page.value = 1; fetchPosts() })
watch(page, fetchPosts)

let searchTimer: ReturnType<typeof setTimeout>
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; fetchPosts() }, 400)
}

function gotoEdit(id?: number) {
  router.push(id ? `/posts/${id}/edit` : '/posts/new')
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

const STATUS_LABEL: Record<string, string> = { draft: '草稿', published: '已发布', archived: '已归档' }
const STATUS_CLASS: Record<string, string> = { draft: 'badge-draft', published: 'badge-published', archived: 'badge-archived' }

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}
</script>

<template>
  <div class="page">

    <!-- 页头 -->
    <div class="page-head">
      <div>
        <h2 class="page-title">文章列表</h2>
        <p class="page-sub">共 {{ total }} 篇文章</p>
      </div>
      <button class="btn-new" @click="gotoEdit()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新建文章
      </button>
    </div>

    <!-- 内容卡片 -->
    <div class="card">

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="search-wrap">
          <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            v-model="search"
            class="search-input"
            placeholder="搜索标题或内容…"
            @input="onSearchInput"
          />
        </div>
        <select v-model="filterCategoryId" class="filter-select">
          <option value="">全部分类</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.label }}</option>
        </select>
        <select v-model="filterStatus" class="filter-select">
          <option value="">全部状态</option>
          <option value="draft">草稿</option>
          <option value="published">已发布</option>
          <option value="archived">已归档</option>
        </select>
      </div>

      <!-- 表格 -->
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
          <!-- 加载中 -->
          <tr v-if="loading">
            <td colspan="5" class="td-center">
              <span class="loading-dot"/>
              <span class="loading-dot"/>
              <span class="loading-dot"/>
            </td>
          </tr>

          <!-- 空状态 -->
          <tr v-else-if="posts.length === 0">
            <td colspan="5" class="td-empty">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              <span>暂无文章，<button class="link-btn" @click="gotoEdit()">立即创建</button></span>
            </td>
          </tr>

          <!-- 数据行 -->
          <tr v-else v-for="post in posts" :key="post.id" class="data-row">
            <td class="td-title" :title="post.title">{{ post.title }}</td>
            <td class="td-meta">{{ post.category?.name ?? '—' }}</td>
            <td>
              <span class="badge" :class="STATUS_CLASS[post.status]">
                {{ STATUS_LABEL[post.status] ?? post.status }}
              </span>
            </td>
            <td class="td-meta">{{ formatDate(post.createdAt) }}</td>
            <td>
              <div class="td-actions">
                <button class="act-btn" @click="gotoEdit(post.id)">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  编辑
                </button>
                <button class="act-btn danger" @click="deleteTarget = post">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页</span>
        <div class="page-btns">
          <button class="page-btn" :disabled="page <= 1" @click="page--">‹</button>
          <button
            v-for="p in totalPages" :key="p"
            class="page-btn" :class="{ active: p === page }"
            @click="page = p"
          >{{ p }}</button>
          <button class="page-btn" :disabled="page >= totalPages" @click="page++">›</button>
        </div>
      </div>

    </div><!-- /card -->

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-mask" @click.self="deleteTarget = null">
        <div class="modal">
          <div class="modal-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <p class="modal-title">确认删除</p>
          <p class="modal-msg">「{{ deleteTarget.title }}」删除后不可恢复。</p>
          <div class="modal-actions">
            <button class="m-btn" @click="deleteTarget = null">取消</button>
            <button class="m-btn m-btn-danger" :disabled="deleting" @click="doDelete">
              {{ deleting ? '删除中…' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<style scoped>
.page {
  padding: 20px;
  min-height: calc(100vh - 76px);
  background: var(--bg-surface, #fff);
  border-radius: 12px;
  box-sizing: border-box;
}

/* ── 页头 ── */
.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-1, #111827);
  margin: 0 0 2px;
}

.page-sub {
  font-size: 12px;
  color: var(--text-3, #9ca3af);
  margin: 0;
}

.btn-new {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 14px;
  background: var(--accent, #6366f1);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.btn-new:hover { opacity: 0.88; }

/* ── 内容卡片 ── */
.card {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px;
  overflow: hidden;
}

/* ── 筛选栏 ── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border, #e5e7eb);
  flex-wrap: wrap;
  background: var(--bg-page, #f9fafb);
}

.search-wrap {
  position: relative;
  flex: 1;
  min-width: 160px;
  max-width: 280px;
}

.search-icon {
  position: absolute;
  left: 9px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-3, #9ca3af);
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 32px;
  padding: 0 10px 0 30px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 7px;
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: var(--accent, #6366f1); }

.filter-select {
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 7px;
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 13px;
  cursor: pointer;
  outline: none;
  min-width: 100px;
}

/* ── 表格 ── */
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th {
  padding: 10px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-3, #9ca3af);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: var(--bg-page, #f9fafb);
  border-bottom: 1px solid var(--border, #e5e7eb);
  white-space: nowrap;
}

.table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border, #e5e7eb);
  color: var(--text-1, #111827);
  vertical-align: middle;
}

.table tbody tr:last-child td { border-bottom: none; }

.data-row { transition: background 0.12s; }
.data-row:hover td { background: var(--bg-hover, #f5f5ff); }

.td-title {
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
  color: var(--text-1, #111827);
}

.td-meta { color: var(--text-2, #6b7280); }

/* 加载动画 */
.td-center { text-align: center; padding: 32px !important; }

.loading-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin: 0 3px;
  border-radius: 50%;
  background: var(--accent, #6366f1);
  animation: pulse 1.2s ease-in-out infinite;
}
.loading-dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse { 0%,80%,100% { opacity: .3; transform: scale(.8); } 40% { opacity: 1; transform: scale(1); } }

/* 空状态 */
.td-empty {
  text-align: center;
  padding: 48px 16px !important;
  color: var(--text-3, #9ca3af);
}
.td-empty { display: table-cell; }
.td-empty svg { display: block; margin: 0 auto 10px; }
.td-empty span { font-size: 13px; }

.link-btn {
  background: none;
  border: none;
  color: var(--accent, #6366f1);
  cursor: pointer;
  font-size: 13px;
  padding: 0;
  text-decoration: underline;
}

/* 状态徽章 */
.badge {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.badge-draft     { background: #f3f4f6; color: #6b7280; }
.badge-published { background: #ecfdf5; color: #059669; }
.badge-archived  { background: #fef3c7; color: #b45309; }

/* 操作按钮 */
.td-actions { display: flex; gap: 4px; }

.act-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 9px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 6px;
  background: var(--bg-surface, #fff);
  color: var(--text-2, #6b7280);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.12s;
  white-space: nowrap;
}
.act-btn:hover {
  border-color: var(--accent, #6366f1);
  color: var(--accent, #6366f1);
  background: rgba(99,102,241,.05);
}
.act-btn.danger:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: rgba(239,68,68,.05);
}

/* ── 分页 ── */
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border, #e5e7eb);
  background: var(--bg-page, #f9fafb);
}

.page-info { font-size: 12px; color: var(--text-3, #9ca3af); }

.page-btns { display: flex; gap: 4px; }

.page-btn {
  min-width: 28px;
  height: 28px;
  padding: 0 6px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 6px;
  background: var(--bg-surface, #fff);
  color: var(--text-2, #6b7280);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.12s;
}
.page-btn:hover:not(:disabled) { border-color: var(--accent, #6366f1); color: var(--accent, #6366f1); }
.page-btn.active { background: var(--accent, #6366f1); border-color: var(--accent, #6366f1); color: #fff; }
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* ── 删除确认 ── */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

.modal {
  background: var(--bg-surface, #fff);
  border-radius: 14px;
  padding: 28px 24px 22px;
  width: 340px;
  box-shadow: 0 20px 60px rgba(0,0,0,.18);
  text-align: center;
}

.modal-icon { margin-bottom: 10px; }
.modal-title { font-size: 15px; font-weight: 700; color: var(--text-1, #111); margin: 0 0 6px; }
.modal-msg { font-size: 13px; color: var(--text-2, #6b7280); margin: 0 0 20px; line-height: 1.6; }

.modal-actions { display: flex; gap: 8px; justify-content: center; }

.m-btn {
  flex: 1;
  height: 34px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border, #e5e7eb);
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  transition: background 0.12s;
}
.m-btn:hover { background: var(--bg-hover, #f3f4f6); }
.m-btn-danger { background: #ef4444; color: #fff; border-color: #ef4444; }
.m-btn-danger:hover { opacity: .9; }
.m-btn-danger:disabled { opacity: .5; cursor: not-allowed; }
</style>
