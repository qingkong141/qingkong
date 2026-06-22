<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@yunpan/shared-api'

interface UserItem {
  id: number; username: string; email: string
  isApproved: boolean; storageUsed: number; storageQuota: number
  createdAt: string | null
}

const router = useRouter()
const users = ref<UserItem[]>([])
const loading = ref(false)
const filter = ref('pending')
const error = ref('')
const quotaModal = ref<{ user: UserItem; value: string } | null>(null)
const deleteTarget = ref<UserItem | null>(null)

function fmtSize(b: number) { if (!b) return '0 B'; const u = ['B','KB','MB','GB']; let i = 0, s = b; while (s >= 1024 && i < u.length - 1) { s /= 1024; i++ } return `${s.toFixed(i ? 1 : 0)} ${u[i]}` }
function fmtDate(d: string | null) { if (!d) return '-'; return new Date(d).toLocaleDateString('zh-CN', { year:'numeric', month:'2-digit', day:'2-digit' }) }
function gb(b: number) { return +(b / (1024*1024*1024)).toFixed(1) }

function openQuotaModal(u: UserItem) {
  quotaModal.value = { user: u, value: String(gb(u.storageQuota)) }
}

async function submitQuota() {
  if (!quotaModal.value) return
  const n = parseInt(quotaModal.value.value)
  if (isNaN(n) || n < 0) return
  try {
    await authApi.adminSetQuota(quotaModal.value.user.id, n)
    quotaModal.value = null
    await load()
  } catch (e: any) { error.value = e?.message || '操作失败'; quotaModal.value = null }
}

async function load() {
  loading.value = true
  try { users.value = await authApi.adminListUsers(filter.value) } catch (e: any) { error.value = e?.message || '加载失败'; if (error.value.includes('403')) router.push('/admin') }
  finally { loading.value = false }
}

async function approve(id: number) {
  try { await authApi.adminApproveUser(id); await load() }
  catch (e: any) { error.value = e?.message || '操作失败' }
}

async function disableUser(id: number) {
  try { await authApi.adminDisableUser(id); await load() }
  catch (e: any) { error.value = e?.message || '操作失败' }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  try { await authApi.adminDeleteUser(deleteTarget.value.id); deleteTarget.value = null; await load() }
  catch (e: any) { error.value = e?.message || '操作失败'; deleteTarget.value = null }
}

function changeFilter(f: string) { filter.value = f; load() }

onMounted(load)
</script>

<template>
  <div class="admin-page">
    <div class="page-head">
      <div>
        <h1 class="page-title">用户管理</h1>
        <p class="page-sub">审核新注册用户 · 管理存储配额</p>
      </div>
    </div>

    <div class="filter-bar">
      <button :class="{ active: filter === 'pending' }" @click="changeFilter('pending')">待审核</button>
      <button :class="{ active: filter === 'approved' }" @click="changeFilter('approved')">已通过</button>
      <button :class="{ active: filter === 'all' }" @click="changeFilter('all')">全部</button>
    </div>

    <p v-if="error" class="err">{{ error }}</p>

    <div class="card">
      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="!users.length" class="empty">暂无数据</div>
      <div v-else class="card-body"><table class="table">
        <thead><tr><th>用户名</th><th>邮箱</th><th>用量</th><th>注册时间</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td class="td-name">{{ u.username }}</td>
            <td>{{ u.email }}</td>
            <td class="td-meta"><span class="quota-link" @click="openQuotaModal(u)" title="点击修改配额">{{ fmtSize(u.storageUsed) }} / {{ fmtSize(u.storageQuota) }}</span></td>
            <td class="td-meta">{{ fmtDate(u.createdAt) }}</td>
            <td><span class="badge" :class="u.isApproved ? 'badge-on' : 'badge-off'">{{ u.isApproved ? '已通过' : '待审核' }}</span></td>
            <td class="td-actions">
              <button v-if="!u.isApproved" class="act-btn" @click="approve(u.id)">✅ 通过</button>
              <button v-if="u.isApproved" class="act-btn" @click="disableUser(u.id)">🚫 禁用</button>
              <button class="act-btn danger" @click="deleteTarget = u">✕ 删除</button>
            </td>
          </tr>
        </tbody>
      </table></div>
    </div>

    <!-- 配额弹窗 -->
    <Teleport to="body">
      <div v-if="quotaModal" class="modal-mask" @click.self="quotaModal = null">
        <div class="modal">
          <h3 class="modal-title">修改存储配额</h3>
          <p class="modal-desc">用户：{{ quotaModal.user.username }}</p>
          <div class="modal-field">
            <input
              v-model="quotaModal.value"
              type="number"
              min="0"
              class="modal-input"
              ref="quotaInput"
              @keyup.enter="submitQuota"
            />
            <span class="modal-unit">GB</span>
          </div>
          <p class="modal-hint">当前已用 {{ fmtSize(quotaModal.user.storageUsed) }}</p>
          <div class="modal-actions">
            <button class="m-btn" @click="quotaModal = null">取消</button>
            <button class="m-btn m-btn-primary" @click="submitQuota">确认</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-mask" @click.self="deleteTarget = null">
        <div class="modal">
          <h3 class="modal-title">删除用户</h3>
          <p class="modal-desc">确定要删除用户「{{ deleteTarget.username }}」吗？该操作不可撤销。</p>
          <div class="modal-actions">
            <button class="m-btn" @click="deleteTarget = null">取消</button>
            <button class="m-btn m-btn-danger" @click="confirmDelete">确认删除</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.admin-page { max-width: 900px; margin: 0 auto; }
.page-head { margin-bottom: 20px; }
.page-title { font-size: 17px; font-weight: 700; color: var(--text-1); margin: 0 0 4px; }
.page-sub { font-size: 12px; color: var(--text-3); margin: 0; }
.err { font-size: 12px; color: #ef4444; margin: 0 0 12px; }

.filter-bar { display: flex; gap: 4px; margin-bottom: 16px; }
.filter-bar button {
  height: 32px; padding: 0 14px; border: 1px solid var(--border); border-radius: 8px;
  background: var(--bg-surface); color: var(--text-2); font-size: 12px; cursor: pointer; transition: all .12s;
}
.filter-bar button:hover { border-color: var(--accent); color: var(--accent); }
.filter-bar button.active { background: var(--accent); color: #fff; border-color: var(--accent); }

.card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.card-body { max-height: calc(100vh - 220px); overflow-y: auto; }
.card-body .table th { position: sticky; top: 0; z-index: 1; }
.empty { padding: 60px 20px; text-align: center; color: var(--text-3); font-size: 13px; }

.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th { padding: 10px 20px; text-align: left; font-size: 11px; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: .06em; background: var(--bg-page); border-bottom: 1px solid var(--border); white-space: nowrap; }
.table td { padding: 10px 20px; border-bottom: 1px solid var(--border); vertical-align: middle; color: var(--text-1); }
.table tbody tr:last-child td { border-bottom: none; }
.td-name { font-weight: 500; }
.td-meta { color: var(--text-2); font-size: 12px; white-space: nowrap; }
.td-actions { white-space: nowrap; }
.td-actions .act-btn + .act-btn { margin-left: 6px; }

.badge { display: inline-block; padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-on { background: #ecfdf5; color: #059669; }
.badge-off { background: #fef3c7; color: #d97706; }

.act-btn {
  display: inline-flex; align-items: center; gap: 4px; padding: 4px 9px;
  border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg-surface); color: var(--text-2); font-size: 12px;
  cursor: pointer; transition: all .12s; white-space: nowrap;
}
.act-btn:hover { border-color: var(--accent); color: var(--accent); background: rgba(99,102,241,.05); }
.act-btn.danger:hover { border-color: #ef4444; color: #ef4444; background: rgba(239,68,68,.05); }
.quota-link { cursor: pointer; border-bottom: 1px dashed var(--text-3); transition: all .12s }
.quota-link:hover { color: var(--accent); border-color: var(--accent) }

/* ── 弹窗 ── */
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; align-items: center; justify-content: center; z-index: 9999; backdrop-filter: blur(2px) }
.modal { background: var(--bg-surface); border-radius: 14px; padding: 24px; width: 360px; box-shadow: 0 20px 60px rgba(0,0,0,.18) }
.modal-title { font-size: 15px; font-weight: 700; color: var(--text-1); margin: 0 0 6px }
.modal-desc { font-size: 13px; color: var(--text-2); margin: 0 0 16px }
.modal-hint { font-size: 12px; color: var(--text-3); margin: 6px 0 0 }
.modal-field { display: flex; gap: 8px; align-items: center }
.modal-input { flex: 1; height: 38px; padding: 0 12px; border: 1.5px solid var(--border); border-radius: 9px; font-size: 14px; outline: none; background: var(--bg-surface); color: var(--text-1) }
.modal-input:focus { border-color: var(--accent) }
.modal-unit { font-size: 13px; color: var(--text-2); font-weight: 500 }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 18px }
.m-btn { height: 34px; padding: 0 16px; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; border: 1px solid var(--border); background: var(--bg-surface); color: var(--text-1); transition: all .12s }
.m-btn:hover { background: var(--bg-hover) }
.m-btn-primary { background: var(--accent); color: #fff; border-color: var(--accent) }
.m-btn-primary:hover { opacity: .9 }
.m-btn-danger { background: #ef4444; color: #fff; border-color: #ef4444 }
.m-btn-danger:hover { opacity: .9 }
</style>
