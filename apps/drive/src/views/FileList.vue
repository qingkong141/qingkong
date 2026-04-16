<script setup lang="ts">
import { ref } from 'vue'
import { fileApi, shareApi } from '@qingkong/shared-api'
import type { FileItem } from '@qingkong/shared-api'
import FilePreview from '../components/FilePreview.vue'
import { useToast } from '../composables/useToast'
import { useConfirm } from '../composables/useConfirm'

const toast = useToast()
const cfm = useConfirm()

interface BreadcrumbItem { id: number | null; name: string }
interface UploadTask { name: string; progress: number; status: 'uploading' | 'done' | 'error' }

const files = ref<FileItem[]>([])
const loading = ref(false)
const currentParentId = ref<number | null>(null)
const breadcrumbs = ref<BreadcrumbItem[]>([{ id: null, name: '全部文件' }])
const viewMode = ref<'list' | 'grid'>('list')
const showNewFolder = ref(false)
const newFolderName = ref('')
const uploads = ref<UploadTask[]>([])
const dragging = ref(false)

const ctx = ref<{ show: boolean; x: number; y: number; file: FileItem | null }>({ show: false, x: 0, y: 0, file: null })
const renaming = ref<{ id: number; name: string } | null>(null)
const showMoveDialog = ref(false)
const moveTarget = ref<FileItem | null>(null)
const moveParentId = ref<number | null>(null)
const showShareDialog = ref(false)
const shareFile = ref<FileItem | null>(null)
const sharePassword = ref('')
const shareExpireHours = ref<number | null>(null)
const preview = ref<{ show: boolean; url: string; name: string; mimeType: string | null }>({ show: false, url: '', name: '', mimeType: null })

async function loadFiles() {
  loading.value = true
  try { files.value = await fileApi.list(currentParentId.value) }
  catch { files.value = [] }
  finally { loading.value = false }
}

async function openFile(file: FileItem) {
  if (file.isDir) {
    currentParentId.value = file.id
    breadcrumbs.value.push({ id: file.id, name: file.name })
    loadFiles()
    return
  }
  try {
    const { url } = await fileApi.download(file.id)
    preview.value = { show: true, url, name: file.name, mimeType: file.mimeType }
  } catch (e: any) { toast.error(e.message || '无法预览') }
}

function navBreadcrumb(i: number) {
  currentParentId.value = breadcrumbs.value[i].id
  breadcrumbs.value = breadcrumbs.value.slice(0, i + 1)
  loadFiles()
}

async function createFolder() {
  const name = newFolderName.value.trim()
  if (!name) return
  try {
    await fileApi.createFolder(name, currentParentId.value)
    newFolderName.value = ''
    showNewFolder.value = false
    loadFiles()
    toast.success('文件夹已创建')
  } catch (e: any) { toast.error(e.message || '创建失败') }
}

const CHUNK = 5 * 1024 * 1024
async function handleUpload(list: FileList | File[]) {
  for (const f of Array.from(list)) {
    const t: UploadTask = { name: f.name, progress: 0, status: 'uploading' }
    uploads.value.push(t)
    try {
      if (f.size <= CHUNK) {
        await fileApi.upload(f, currentParentId.value, p => { t.progress = p })
      } else {
        const total = Math.ceil(f.size / CHUNK)
        const { uploadId } = await fileApi.multipartInit(f.name, f.size, total, currentParentId.value)
        for (let i = 0; i < total; i++) {
          await fileApi.multipartChunk(uploadId, i, f.slice(i * CHUNK, i * CHUNK + CHUNK))
          t.progress = Math.round(((i + 1) / total) * 100)
        }
        await fileApi.multipartComplete(uploadId)
      }
      t.status = 'done'; t.progress = 100
      loadFiles()
    } catch { t.status = 'error' }
  }
}
function onFileInput(e: Event) { const el = e.target as HTMLInputElement; if (el.files) handleUpload(el.files); el.value = '' }
function onDrop(e: DragEvent) { dragging.value = false; if (e.dataTransfer?.files) handleUpload(e.dataTransfer.files) }
function clearDone() { uploads.value = uploads.value.filter(t => t.status === 'uploading') }

function onCtx(e: MouseEvent, f: FileItem) { e.preventDefault(); ctx.value = { show: true, x: e.clientX, y: e.clientY, file: f } }
function closeCtx() { ctx.value.show = false }

async function handleDownload() { const f = ctx.value.file; closeCtx(); if (!f || f.isDir) return; try { const { url } = await fileApi.download(f.id); window.open(url, '_blank') } catch (e: any) { toast.error(e.message) } }
function startRename() { const f = ctx.value.file; closeCtx(); if (f) renaming.value = { id: f.id, name: f.name } }
async function submitRename() { if (!renaming.value) return; try { await fileApi.rename(renaming.value.id, renaming.value.name); renaming.value = null; loadFiles(); toast.success('已重命名') } catch (e: any) { toast.error(e.message) } }
function startMove() { moveTarget.value = ctx.value.file; closeCtx(); moveParentId.value = null; showMoveDialog.value = true }
async function submitMove() { if (!moveTarget.value) return; try { await fileApi.move(moveTarget.value.id, moveParentId.value); showMoveDialog.value = false; moveTarget.value = null; loadFiles(); toast.success('已移动') } catch (e: any) { toast.error(e.message) } }

async function handleDelete() {
  const f = ctx.value.file; closeCtx(); if (!f) return
  if (!await cfm.open({ title: '删除文件', message: `确定删除「${f.name}」？将移入回收站`, confirmText: '删除', danger: true })) return
  try { await fileApi.delete(f.id); loadFiles(); toast.success('已移入回收站') } catch (e: any) { toast.error(e.message) }
}

function startShare() { shareFile.value = ctx.value.file; closeCtx(); sharePassword.value = ''; shareExpireHours.value = null; showShareDialog.value = true }
async function submitShare() {
  if (!shareFile.value) return
  try {
    const s = await shareApi.create(shareFile.value.id, sharePassword.value || null, shareExpireHours.value)
    await navigator.clipboard.writeText(`${window.location.origin}/s/${s.token}`)
    toast.success('分享链接已复制'); showShareDialog.value = false
  } catch (e: any) { toast.error(e.message) }
}

function fmtSize(b: number) { if (!b) return '-'; const u = ['B','KB','MB','GB']; let i = 0, s = b; while (s >= 1024 && i < u.length - 1) { s /= 1024; i++ } return `${s.toFixed(i ? 1 : 0)} ${u[i]}` }
function fmtDate(d: string) { return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }
function icon(f: FileItem) { if (f.isDir) return '📁'; const m = f.mimeType || ''; if (m.startsWith('image/')) return '🖼️'; if (m.startsWith('video/')) return '🎬'; if (m.startsWith('audio/')) return '🎵'; if (m === 'application/pdf') return '📄'; if (/zip|rar|tar/.test(m)) return '📦'; return '📃' }

loadFiles()
</script>

<template>
  <div @click="closeCtx">
    <!-- Head -->
    <div class="page-head">
      <div>
        <h1 class="page-title">文件管理</h1>
        <p class="page-sub">
          <span v-for="(bc, i) in breadcrumbs" :key="i">
            <a v-if="i < breadcrumbs.length - 1" class="bc-link" @click.stop="navBreadcrumb(i)">{{ bc.name }}</a>
            <span v-else class="bc-cur">{{ bc.name }}</span>
            <span v-if="i < breadcrumbs.length - 1" class="bc-sep"> / </span>
          </span>
        </p>
      </div>
      <div class="head-actions">
        <button class="act-btn" @click="showNewFolder = true">+ 新建文件夹</button>
        <label class="btn-new"><span>⬆ 上传文件</span><input type="file" multiple hidden @change="onFileInput" /></label>
        <button class="act-btn icon-only" @click="viewMode = viewMode === 'list' ? 'grid' : 'list'">{{ viewMode === 'list' ? '▦' : '☰' }}</button>
      </div>
    </div>

    <!-- New Folder -->
    <div v-if="showNewFolder" class="nf-bar">
      <input v-model="newFolderName" class="form-input nf-input" placeholder="文件夹名称" @keyup.enter="createFolder" @keyup.esc="showNewFolder = false" />
      <button class="btn-new" @click="createFolder">确定</button>
      <button class="act-btn" @click="showNewFolder = false">取消</button>
    </div>

    <!-- Card -->
    <div class="card" :class="{ 'drag-over': dragging }" @dragover.prevent="dragging = true" @dragleave="dragging = false" @drop.prevent="onDrop">
      <div v-if="dragging" class="drop-hint">释放文件以上传</div>

      <div v-if="loading" class="empty-state">加载中…</div>
      <div v-else-if="!files.length" class="empty-state"><span class="empty-icon">📂</span><br/>拖拽文件到此处，或点击上方上传</div>

      <!-- List -->
      <table v-else-if="viewMode === 'list'" class="table">
        <thead><tr><th>名称</th><th>大小</th><th>修改时间</th></tr></thead>
        <tbody>
          <tr v-for="f in files" :key="f.id" class="data-row" @dblclick="openFile(f)" @contextmenu="onCtx($event, f)">
            <td class="td-name">
              <span class="fi">{{ icon(f) }}</span>
              <template v-if="renaming?.id === f.id">
                <input v-model="renaming.name" class="form-input rename-inp" @keyup.enter="submitRename" @keyup.esc="renaming = null" @blur="submitRename" />
              </template>
              <span v-else class="fn">{{ f.name }}</span>
            </td>
            <td class="td-meta">{{ f.isDir ? '-' : fmtSize(f.size) }}</td>
            <td class="td-meta">{{ fmtDate(f.updatedAt) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Grid -->
      <div v-else class="grid">
        <div v-for="f in files" :key="f.id" class="grid-card" @dblclick="openFile(f)" @contextmenu="onCtx($event, f)">
          <div class="gc-icon">{{ icon(f) }}</div>
          <div class="gc-name" :title="f.name">{{ f.name }}</div>
        </div>
      </div>
    </div>

    <!-- Upload Panel -->
    <div v-if="uploads.length" class="up-panel">
      <div class="up-head"><span>上传任务</span><a class="link-btn" @click="clearDone">清除已完成</a></div>
      <div v-for="(t, i) in uploads" :key="i" class="up-row">
        <span class="up-name">{{ t.name }}</span>
        <div class="up-track"><div class="up-fill" :class="t.status" :style="{ width: t.progress + '%' }" /></div>
        <span class="up-pct">{{ t.status === 'error' ? '失败' : t.progress + '%' }}</span>
      </div>
    </div>

    <!-- Context Menu -->
    <Teleport to="body">
      <div v-if="ctx.show" class="ctx" :style="{ left: ctx.x + 'px', top: ctx.y + 'px' }">
        <div v-if="!ctx.file?.isDir" class="ctx-item" @click="handleDownload">⬇ 下载</div>
        <div class="ctx-item" @click="startRename">✏️ 重命名</div>
        <div class="ctx-item" @click="startMove">📂 移动到</div>
        <div class="ctx-item" @click="startShare">🔗 创建分享</div>
        <div class="ctx-item danger" @click="handleDelete">🗑️ 删除</div>
      </div>
    </Teleport>

    <!-- Move Dialog -->
    <Teleport to="body">
      <div v-if="showMoveDialog" class="modal-mask" @click.self="showMoveDialog = false">
        <div class="modal">
          <h3 class="modal-title">移动到</h3>
          <div class="form-group">
            <label class="form-label">目标文件夹 ID（空 = 根目录）</label>
            <input v-model.number="moveParentId" type="number" class="form-input" />
          </div>
          <div class="modal-actions">
            <button class="m-btn" @click="showMoveDialog = false">取消</button>
            <button class="m-btn m-btn-primary" @click="submitMove">移动</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Share Dialog -->
    <Teleport to="body">
      <div v-if="showShareDialog" class="modal-mask" @click.self="showShareDialog = false">
        <div class="modal">
          <h3 class="modal-title">创建分享</h3>
          <p class="share-file-hint">{{ shareFile?.name }}</p>
          <div class="form-group">
            <label class="form-label">提取密码（可选）</label>
            <input v-model="sharePassword" class="form-input" placeholder="留空则无需密码" />
          </div>
          <div class="form-group">
            <label class="form-label">有效期</label>
            <select v-model="shareExpireHours" class="form-input">
              <option :value="null">永不过期</option>
              <option :value="1">1 小时</option>
              <option :value="24">1 天</option>
              <option :value="168">7 天</option>
              <option :value="720">30 天</option>
            </select>
          </div>
          <div class="modal-actions">
            <button class="m-btn" @click="showShareDialog = false">取消</button>
            <button class="m-btn m-btn-primary" @click="submitShare">创建并复制链接</button>
          </div>
        </div>
      </div>
    </Teleport>

    <FilePreview v-if="preview.show" :url="preview.url" :name="preview.name" :mime-type="preview.mimeType" @close="preview.show = false" />
  </div>
</template>

<style scoped>
/* ── Page Head ── */
.page-head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; }
.page-title { font-size: 17px; font-weight: 700; color: var(--text-1, #111827); margin: 0 0 2px; }
.page-sub { font-size: 12px; color: var(--text-3, #9ca3af); margin: 0; }
.bc-link { color: var(--accent, #6366f1); cursor: pointer; text-decoration: none; }
.bc-link:hover { text-decoration: underline; }
.bc-cur { color: var(--text-1, #111827); font-weight: 500; }
.bc-sep { color: var(--text-3, #9ca3af); }
.head-actions { display: flex; gap: 8px; align-items: center; }

/* ── Buttons ── */
.btn-new {
  display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px;
  background: var(--accent, #6366f1); color: #fff; border: none; border-radius: 8px;
  font-size: 13px; font-weight: 500; cursor: pointer; transition: opacity 0.15s; white-space: nowrap;
}
.btn-new:hover { opacity: 0.88; }

.act-btn {
  display: inline-flex; align-items: center; gap: 4px; height: 34px; padding: 0 12px;
  border: 1px solid var(--border, #e5e7eb); border-radius: 8px;
  background: var(--bg-surface, #fff); color: var(--text-2, #6b7280); font-size: 13px;
  cursor: pointer; transition: all 0.12s; white-space: nowrap;
}
.act-btn:hover { border-color: var(--accent, #6366f1); color: var(--accent, #6366f1); background: rgba(99,102,241,.05); }
.act-btn.icon-only { padding: 0 10px; font-size: 16px; }

.link-btn { background: none; border: none; color: var(--accent, #6366f1); cursor: pointer; font-size: 12px; padding: 0; }

/* ── New Folder ── */
.nf-bar { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; }
.nf-input { flex: 1; max-width: 260px; }

/* ── Card ── */
.card {
  position: relative; background: var(--bg-surface, #fff); border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px; overflow: hidden; min-height: 260px;
}
.card.drag-over { outline: 2px dashed var(--accent, #6366f1); outline-offset: -3px; }
.drop-hint {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(99,102,241,.06); font-size: 14px; color: var(--accent, #6366f1); font-weight: 500; z-index: 5; pointer-events: none;
}
.empty-state { padding: 60px 16px; text-align: center; color: var(--text-3, #9ca3af); font-size: 13px; line-height: 1.8; }
.empty-icon { font-size: 40px; }

/* ── Table ── */
.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th {
  padding: 10px 16px; text-align: left; font-size: 11px; font-weight: 600;
  color: var(--text-3, #9ca3af); text-transform: uppercase; letter-spacing: 0.06em;
  background: var(--bg-page, #f9fafb); border-bottom: 1px solid var(--border, #e5e7eb); white-space: nowrap;
}
.table td { padding: 10px 16px; border-bottom: 1px solid var(--border, #e5e7eb); vertical-align: middle; }
.table tbody tr:last-child td { border-bottom: none; }
.data-row { cursor: pointer; transition: background 0.12s; }
.data-row:hover { background: var(--bg-hover, #f5f5ff); }

.td-name { display: flex; align-items: center; gap: 8px; font-weight: 500; color: var(--text-1, #111827); }
.fi { font-size: 17px; flex-shrink: 0; }
.fn { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-meta { color: var(--text-2, #6b7280); white-space: nowrap; }

.rename-inp { width: 200px; height: 28px; font-size: 13px; }

/* ── Grid ── */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 4px; padding: 12px; }
.grid-card {
  display: flex; flex-direction: column; align-items: center; padding: 14px 6px 10px;
  border-radius: 8px; cursor: pointer; transition: background 0.12s;
}
.grid-card:hover { background: var(--bg-hover, #f5f5ff); }
.gc-icon { font-size: 32px; margin-bottom: 6px; }
.gc-name { font-size: 11px; color: var(--text-1, #111827); text-align: center; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── Upload Panel ── */
.up-panel {
  position: fixed; bottom: 16px; right: 16px; width: 300px;
  background: var(--bg-surface, #fff); border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,.1); padding: 14px; z-index: 100;
}
.up-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 13px; font-weight: 600; color: var(--text-1, #111); }
.up-row { margin-bottom: 8px; }
.up-name { display: block; font-size: 12px; color: var(--text-2, #6b7280); margin-bottom: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.up-track { height: 3px; background: var(--bg-page, #f3f4f6); border-radius: 2px; overflow: hidden; }
.up-fill { height: 100%; border-radius: 2px; transition: width 0.2s; }
.up-fill.uploading { background: var(--accent, #6366f1); }
.up-fill.done { background: #22c55e; }
.up-fill.error { background: #ef4444; }
.up-pct { font-size: 11px; color: var(--text-3, #9ca3af); }

/* ── Context Menu ── */
.ctx {
  position: fixed; min-width: 150px; background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e5e7eb); border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,.12); padding: 4px 0; z-index: 200;
}
.ctx-item { padding: 8px 14px; font-size: 13px; cursor: pointer; color: var(--text-1, #111); transition: background 0.1s; }
.ctx-item:hover { background: var(--bg-hover, #f5f5ff); }
.ctx-item.danger { color: #ef4444; }

/* ── Modal ── */
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,.45); display: flex; align-items: center; justify-content: center; z-index: 9999; backdrop-filter: blur(2px); }
.modal { background: var(--bg-surface, #fff); border-radius: 14px; padding: 24px; width: 380px; box-shadow: 0 20px 60px rgba(0,0,0,.18); }
.modal-title { font-size: 15px; font-weight: 700; color: var(--text-1, #111); margin: 0 0 14px; }
.share-file-hint { font-size: 13px; color: var(--text-2, #6b7280); margin: 0 0 14px; word-break: break-all; }
.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 12px; font-weight: 600; color: var(--text-2, #6b7280); margin-bottom: 5px; }
.form-input {
  width: 100%; height: 34px; padding: 0 10px; border: 1px solid var(--border, #e5e7eb); border-radius: 7px;
  background: var(--bg-surface, #fff); color: var(--text-1, #111); font-size: 13px; outline: none;
  box-sizing: border-box; transition: border-color 0.15s, box-shadow 0.15s;
}
.form-input:focus { border-color: var(--accent, #6366f1); box-shadow: 0 0 0 3px rgba(99,102,241,.1); }
select.form-input { cursor: pointer; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 18px; }
.m-btn {
  height: 34px; padding: 0 16px; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer;
  border: 1px solid var(--border, #e5e7eb); background: var(--bg-surface, #fff); color: var(--text-1, #111); transition: background 0.12s;
}
.m-btn:hover { background: var(--bg-hover, #f3f4f6); }
.m-btn.m-btn-primary { background: var(--accent, #6366f1); color: #fff; border-color: var(--accent, #6366f1); }
.m-btn.m-btn-primary:hover { background: var(--accent, #6366f1); opacity: .9; }
</style>
