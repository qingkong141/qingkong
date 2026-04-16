<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { commentApi } from '@qingkong/shared-api'
import type { CommentWithPost } from '@qingkong/shared-api'
import { showToast } from '../composables/toast'

const comments = ref<CommentWithPost[]>([])
const total = ref(0)
const loading = ref(false)

const page = ref(1)
const PAGE_SIZE = 20
const filterStatus = ref('')
const search = ref('')

const totalPages = computed(() => Math.ceil(total.value / PAGE_SIZE))

const deleteTarget = ref<CommentWithPost | null>(null)
const deleting = ref(false)

async function fetchComments() {
  loading.value = true
  try {
    const res = await commentApi.list({
      page: page.value,
      pageSize: PAGE_SIZE,
      status: filterStatus.value || undefined,
      search: search.value || undefined,
    })
    comments.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

onMounted(fetchComments)

watch([filterStatus], () => { page.value = 1; fetchComments() })
watch(page, fetchComments)

let searchTimer: ReturnType<typeof setTimeout>
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; fetchComments() }, 400)
}

async function approve(c: CommentWithPost) {
  try {
    await commentApi.updateStatus(c.id, 'approved')
    showToast('评论已通过', 'success')
    fetchComments()
  } catch {
    showToast('操作失败', 'error')
  }
}

async function reject(c: CommentWithPost) {
  try {
    await commentApi.updateStatus(c.id, 'pending')
    showToast('评论已设为待审', 'success')
    fetchComments()
  } catch {
    showToast('操作失败', 'error')
  }
}

async function doDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await commentApi.delete(deleteTarget.value.id)
    showToast('评论已删除', 'success')
    deleteTarget.value = null
    fetchComments()
  } catch {
    showToast('删除失败', 'error')
  } finally {
    deleting.value = false
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

const STATUS_LABEL: Record<string, string> = { pending: '待审核', approved: '已通过' }
const STATUS_CLASS: Record<string, string> = { pending: 'badge-pending', approved: 'badge-approved' }
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2 class="page-title">评论管理</h2>
        <p class="page-sub">共 {{ total }} 条评论</p>
      </div>
    </div>

    <div class="card">
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="search-wrap">
          <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            v-model="search"
            class="search-input"
            placeholder="搜索评论内容…"
            @input="onSearchInput"
          />
        </div>
        <select v-model="filterStatus" class="filter-select">
          <option value="">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
        </select>
      </div>

      <!-- 列表 -->
      <div class="comment-list">
        <!-- 加载中 -->
        <div v-if="loading" class="center-state">
          <span class="loading-dot"/><span class="loading-dot"/><span class="loading-dot"/>
        </div>

        <!-- 空 -->
        <div v-else-if="comments.length === 0" class="center-state empty">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.3"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span>暂无评论</span>
        </div>

        <!-- 评论卡片 -->
        <div v-else v-for="c in comments" :key="c.id" class="comment-card">
          <div class="comment-top">
            <div class="comment-author">
              <div class="avatar">
                <img v-if="c.author?.avatar" :src="c.author.avatar" class="avatar-img" />
                <span v-else class="avatar-letter">{{ c.author?.username?.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="author-info">
                <span class="author-name">{{ c.author?.username ?? '未知用户' }}</span>
                <span class="comment-time">{{ formatDate(c.createdAt) }}</span>
              </div>
            </div>
            <span class="badge" :class="STATUS_CLASS[c.status]">{{ STATUS_LABEL[c.status] ?? c.status }}</span>
          </div>
          <div class="comment-post" v-if="c.postTitle">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            {{ c.postTitle }}
          </div>
          <div class="comment-content">{{ c.content }}</div>
          <div class="comment-actions">
            <button v-if="c.status === 'pending'" class="act-btn approve" @click="approve(c)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              通过
            </button>
            <button v-if="c.status === 'approved'" class="act-btn" @click="reject(c)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
              撤回
            </button>
            <button class="act-btn danger" @click="deleteTarget = c">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
              删除
            </button>
          </div>
        </div>
      </div>

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
    </div>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-mask" @click.self="deleteTarget = null">
        <div class="modal">
          <div class="modal-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <p class="modal-title">确认删除</p>
          <p class="modal-msg">删除此评论后不可恢复。</p>
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

.card {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px;
  overflow: hidden;
}

/* 筛选栏 */
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

/* 评论列表 */
.comment-list {
  display: flex;
  flex-direction: column;
}

.center-state {
  text-align: center;
  padding: 48px 16px;
  color: var(--text-3, #9ca3af);
}
.center-state svg { display: block; margin: 0 auto 10px; }
.center-state span { font-size: 13px; }

.loading-dot {
  display: inline-block;
  width: 6px; height: 6px;
  margin: 0 3px;
  border-radius: 50%;
  background: var(--accent, #6366f1);
  animation: pulse 1.2s ease-in-out infinite;
}
.loading-dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse { 0%,80%,100% { opacity: .3; transform: scale(.8); } 40% { opacity: 1; transform: scale(1); } }

/* 评论卡片 */
.comment-card {
  padding: 16px;
  border-bottom: 1px solid var(--border, #e5e7eb);
  transition: background 0.12s;
}
.comment-card:last-child { border-bottom: none; }
.comment-card:hover { background: var(--bg-hover, #f5f5ff); }

.comment-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 30px;
  height: 30px;
  flex-shrink: 0;
}

.avatar-img {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-letter {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent, #6366f1), #a78bfa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.author-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-1, #111827);
}

.comment-time {
  font-size: 11px;
  color: var(--text-3, #9ca3af);
}

/* 文章来源 */
.comment-post {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-3, #9ca3af);
  margin-bottom: 8px;
  padding-left: 40px;
}

.comment-content {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-1, #111827);
  padding-left: 40px;
  margin-bottom: 10px;
  word-break: break-word;
}

.comment-actions {
  display: flex;
  gap: 4px;
  padding-left: 40px;
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
.badge-pending  { background: #fef3c7; color: #b45309; }
.badge-approved { background: #ecfdf5; color: #059669; }

/* 操作按钮 */
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
.act-btn.approve:hover {
  border-color: #059669;
  color: #059669;
  background: rgba(5,150,105,.05);
}
.act-btn.danger:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: rgba(239,68,68,.05);
}

/* 分页 */
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

/* 弹窗 */
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
