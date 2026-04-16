<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { shareApi } from '@qingkong/shared-api'
import type { ShareItem } from '@qingkong/shared-api'
import { useToast } from '../composables/useToast'
import { useConfirm } from '../composables/useConfirm'

const toast = useToast()
const cfm = useConfirm()
const shares = ref<ShareItem[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try { shares.value = await shareApi.list() }
  catch { shares.value = [] }
  finally { loading.value = false }
}

async function remove(id: number) {
  if (!await cfm.open({ title: '取消分享', message: '取消后他人将无法访问此链接', confirmText: '取消分享', danger: true })) return
  try { await shareApi.delete(id); shares.value = shares.value.filter(s => s.id !== id); toast.success('已取消分享') }
  catch (e: any) { toast.error(e.message) }
}

function copyLink(token: string) {
  navigator.clipboard.writeText(`${window.location.origin}/s/${token}`)
  toast.success('链接已复制')
}

function fmtDate(d: string | null) { if (!d) return '永不过期'; return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }) }

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">我的分享</h1>
        <p class="page-sub">管理已创建的分享链接</p>
      </div>
    </div>

    <div class="card">
      <div v-if="loading" class="empty-state">加载中…</div>
      <div v-else-if="!shares.length" class="empty-state"><span class="empty-icon">🔗</span><br/>暂无分享</div>

      <table v-else class="table">
        <thead><tr><th>文件</th><th>密码</th><th>过期时间</th><th>下载</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="s in shares" :key="s.id" class="data-row">
            <td class="td-name"><span class="fi">{{ s.isDir ? '📁' : '📃' }}</span><span class="fn">{{ s.fileName }}</span></td>
            <td class="td-meta">
              <span v-if="s.password" class="pw-text" :title="s.password">{{ s.password }}</span>
              <span v-else class="badge badge-off">无</span>
            </td>
            <td class="td-meta">{{ fmtDate(s.expireAt) }}</td>
            <td class="td-meta">{{ s.downloadCount }}</td>
            <td class="td-actions">
              <button class="act-btn" @click="copyLink(s.token)">📋 复制链接</button>
              <button class="act-btn danger-text" @click="remove(s.id)">✕ 取消</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page-head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; }
.page-title { font-size: 17px; font-weight: 700; color: var(--text-1, #111827); margin: 0 0 2px; }
.page-sub { font-size: 12px; color: var(--text-3, #9ca3af); margin: 0; }

.card { background: var(--bg-surface, #fff); border: 1px solid var(--border, #e5e7eb); border-radius: 12px; overflow: hidden; }
.empty-state { padding: 60px 16px; text-align: center; color: var(--text-3, #9ca3af); font-size: 13px; line-height: 1.8; }
.empty-icon { font-size: 40px; }

.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th { padding: 10px 16px; text-align: left; font-size: 11px; font-weight: 600; color: var(--text-3, #9ca3af); text-transform: uppercase; letter-spacing: 0.06em; background: var(--bg-page, #f9fafb); border-bottom: 1px solid var(--border, #e5e7eb); white-space: nowrap; }
.table td { padding: 10px 16px; border-bottom: 1px solid var(--border, #e5e7eb); vertical-align: middle; }
.table tbody tr:last-child td { border-bottom: none; }
.data-row { transition: background 0.12s; }
.data-row:hover { background: var(--bg-hover, #f5f5ff); }
.td-name { display: flex; align-items: center; gap: 8px; font-weight: 500; color: var(--text-1, #111827); }
.fi { font-size: 17px; flex-shrink: 0; }
.fn { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-meta { color: var(--text-2, #6b7280); }
.td-actions { display: flex; gap: 4px; }

.pw-text {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px; color: var(--text-1, #111827);
  background: var(--bg-page, #f9fafb); padding: 2px 8px; border-radius: 4px;
  border: 1px solid var(--border, #e5e7eb); user-select: all;
}
.badge { display: inline-block; padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-off { background: #f3f4f6; color: #6b7280; }

.act-btn {
  display: inline-flex; align-items: center; gap: 4px; padding: 4px 9px;
  border: 1px solid var(--border, #e5e7eb); border-radius: 6px;
  background: var(--bg-surface, #fff); color: var(--text-2, #6b7280); font-size: 12px;
  cursor: pointer; transition: all 0.12s; white-space: nowrap;
}
.act-btn:hover { border-color: var(--accent, #6366f1); color: var(--accent, #6366f1); background: rgba(99,102,241,.05); }
.act-btn.danger-text:hover { border-color: #ef4444; color: #ef4444; background: rgba(239,68,68,.05); }
</style>
