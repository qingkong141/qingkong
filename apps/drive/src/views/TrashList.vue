<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fileApi } from '@qingkong/shared-api'
import type { FileItem } from '@qingkong/shared-api'
import { useToast } from '../composables/useToast'
import { useConfirm } from '../composables/useConfirm'

const toast = useToast()
const cfm = useConfirm()
const files = ref<FileItem[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try { files.value = await fileApi.listTrash() }
  catch { files.value = [] }
  finally { loading.value = false }
}

async function restore(id: number) {
  await fileApi.restore(id)
  files.value = files.value.filter(f => f.id !== id)
  toast.success('已还原')
}

async function permanentDel(id: number) {
  if (!await cfm.open({ title: '彻底删除', message: '删除后不可恢复，确定？', confirmText: '彻底删除', danger: true })) return
  try { await fileApi.permanentDelete(id); files.value = files.value.filter(f => f.id !== id); toast.success('已彻底删除') }
  catch (e: any) { toast.error(e.message) }
}

async function emptyAll() {
  if (!await cfm.open({ title: '清空回收站', message: '所有文件将被彻底删除，不可恢复', confirmText: '全部删除', danger: true })) return
  try { await fileApi.emptyTrash(); files.value = []; toast.success('回收站已清空') }
  catch (e: any) { toast.error(e.message) }
}

function fmtSize(b: number) { if (!b) return '-'; const u = ['B','KB','MB','GB']; let i = 0, s = b; while (s >= 1024 && i < u.length - 1) { s /= 1024; i++ } return `${s.toFixed(i ? 1 : 0)} ${u[i]}` }

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">回收站</h1>
        <p class="page-sub">已删除的文件可在此还原或彻底删除</p>
      </div>
      <button v-if="files.length" class="act-btn danger-btn" @click="emptyAll">🗑️ 清空回收站</button>
    </div>

    <div class="card">
      <div v-if="loading" class="empty-state">加载中…</div>
      <div v-else-if="!files.length" class="empty-state"><span class="empty-icon">🗑️</span><br/>回收站为空</div>

      <table v-else class="table">
        <thead><tr><th>名称</th><th>大小</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="f in files" :key="f.id" class="data-row">
            <td class="td-name"><span class="fi">{{ f.isDir ? '📁' : '📃' }}</span><span class="fn">{{ f.name }}</span></td>
            <td class="td-meta">{{ f.isDir ? '-' : fmtSize(f.size) }}</td>
            <td class="td-actions">
              <button class="act-btn" @click="restore(f.id)">↩ 还原</button>
              <button class="act-btn danger-text" @click="permanentDel(f.id)">✕ 彻底删除</button>
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
.data-row:hover td { background: var(--bg-hover, #f5f5ff); }
.td-name { display: flex; align-items: center; gap: 8px; font-weight: 500; color: var(--text-1, #111827); }
.fi { font-size: 17px; flex-shrink: 0; }
.fn { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-meta { color: var(--text-2, #6b7280); }
.td-actions { display: flex; gap: 4px; }

.act-btn {
  display: inline-flex; align-items: center; gap: 4px; padding: 4px 9px;
  border: 1px solid var(--border, #e5e7eb); border-radius: 6px;
  background: var(--bg-surface, #fff); color: var(--text-2, #6b7280); font-size: 12px;
  cursor: pointer; transition: all 0.12s; white-space: nowrap;
}
.act-btn:hover { border-color: var(--accent, #6366f1); color: var(--accent, #6366f1); background: rgba(99,102,241,.05); }

.danger-btn { border-color: #fca5a5; color: #ef4444; }
.danger-btn:hover { border-color: #ef4444; color: #ef4444; background: rgba(239,68,68,.05); }

.danger-text:hover { border-color: #ef4444; color: #ef4444; background: rgba(239,68,68,.05); }
</style>
