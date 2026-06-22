<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiClient } from '@yunpan/shared-api'

interface BrowseItem {
  id: number; name: string; size: number; mimeType: string | null
  isDir: boolean; updatedAt: string | null
}

interface BreadcrumbItem { id: number | null; name: string }

const route = useRoute()
const token = route.params.token as string

const loading = ref(true)
const needPassword = ref(false)
const password = ref('')
const error = ref('')
const fileInfo = ref<{ fileName: string; fileSize: number; isDir: boolean; allowDownload: boolean } | null>(null)

// 单文件预览
const playing = ref(false)
const textContent = ref('')
const textLoading = ref(false)
const previewItem = ref<BrowseItem | null>(null)

// 文件夹浏览
const folderItems = ref<BrowseItem[]>([])
const folderBreadcrumbs = ref<BreadcrumbItem[]>([])
const folderLoading = ref(false)
const folderParentId = ref<number | null>(null)

const streamUrl = computed(() => {
  const fileId = previewItem.value?.id
  const base = `/yunpan/s/${token}/stream`
  let url = fileId ? `${base}?fileId=${fileId}` : base
  if (!password.value) return url
  const sep = url.includes('?') ? '&' : '?'
  return `${url}${sep}password=${encodeURIComponent(password.value)}`
})

// ── 文件类型判断 ──────────────────────
function isVideo(name: string): boolean { const e = name.split('.').pop()?.toLowerCase() || ''; return ['mp4','mov','webm','mkv'].includes(e) }
function isAudio(name: string): boolean { const e = name.split('.').pop()?.toLowerCase() || ''; return ['mp3','wav','ogg','flac','m4a','aac','wma','opus','weba','mid','midi'].includes(e) }
function isImage(name: string): boolean { const e = name.split('.').pop()?.toLowerCase() || ''; return ['jpg','jpeg','png','gif','webp','svg','bmp','ico'].includes(e) }
function isPdf(name: string): boolean   { return name.split('.').pop()?.toLowerCase() === 'pdf' }
function isText(name: string): boolean  { const e = name.split('.').pop()?.toLowerCase() || ''; return ['txt','md','json','xml','html','css','js','ts','jsx','tsx','vue','py','java','go','rs','sh','yml','yaml','toml','ini','cfg','log','sql','env'].includes(e) }
function isOffice(name: string): boolean { const e = name.split('.').pop()?.toLowerCase() || ''; return ['doc','docx','ppt','pptx','xls','xlsx'].includes(e) }
function isPlayable(name: string): boolean { return isVideo(name) || isAudio(name) }
function isPreviewable(name: string): boolean { return isVideo(name) || isAudio(name) || isImage(name) || isPdf(name) || isText(name) }
function previewActionLabel(name: string): string {
  if (isVideo(name)) return '播放视频'
  if (isAudio(name)) return '播放音频'
  if (isImage(name)) return '查看图片'
  if (isPdf(name)) return '查看文档'
  if (isText(name)) return '查看内容'
  return ''
}

function formatSize(bytes: number): string {
  if (bytes === 0) return '-'
  const units = ['B','KB','MB','GB']; let i = 0, s = bytes
  while (s >= 1024 && i < units.length - 1) { s /= 1024; i++ }
  return `${s.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

function fileTypeLabel(name: string, isDir: boolean): string {
  if (isDir) return '文件夹'
  if (isVideo(name)) return '视频文件'; if (isAudio(name)) return '音频文件'
  if (isImage(name)) return '图片'; if (isPdf(name)) return 'PDF 文档'
  if (isOffice(name)) return 'Office 文档'; if (isText(name)) return '文本文件'
  const e = name.split('.').pop()?.toLowerCase() || ''
  return ({zip:'压缩包',rar:'压缩包'})[e] || `${e.toUpperCase()} 文件`
}

// ── 分享加载 ──────────────────────────
async function loadShare(pwd?: string) {
  loading.value = true; error.value = ''
  try {
    const data: any = await apiClient.post(`/s/${token}`, pwd ? { password: pwd } : {})
    if (data.needPassword) { needPassword.value = true; error.value = pwd ? '密码错误' : '' }
    else {
      fileInfo.value = { fileName: data.fileName, fileSize: data.fileSize, isDir: data.isDir, allowDownload: data.allowDownload !== false }
      needPassword.value = false
      if (data.isDir) await loadFolderContents(null, true)
    }
  } catch (e: any) { handleError(e) }
  finally { loading.value = false }
}

function handleError(e: any) {
  const msg = e?.message || '访问失败'
  if (msg.includes('密码')) { needPassword.value = true; error.value = password.value ? '密码错误' : '' }
  else error.value = msg
}

// ── 单文件操作 ────────────────────────
async function downloadFile(fileId?: number) {
  error.value = ''
  try {
    const params: any = password.value ? { password: password.value } : {}
    const data: any = await apiClient.post(`/s/${token}/download${fileId ? `?fileId=${fileId}` : ''}`, params)
    // 用隐藏 iframe 触发下载，不弹窗
    const iframe = document.createElement('iframe')
    iframe.style.display = 'none'
    iframe.src = data.url
    document.body.appendChild(iframe)
    setTimeout(() => document.body.removeChild(iframe), 3000)
  } catch (e: any) { error.value = e?.message || '下载失败' }
}

function startPlay(item?: BrowseItem) {
  error.value = ''
  previewItem.value = item || null
  playing.value = true
  const name = item?.name || fileInfo.value?.fileName || ''
  if (isText(name)) {
    textLoading.value = true; textContent.value = ''
    fetch(streamUrl.value).then(r => r.text()).then(t => { textContent.value = t }).catch(() => { textContent.value = '无法加载文件内容' }).finally(() => { textLoading.value = false })
  }
}

// ── 文件夹浏览 ────────────────────────
async function loadFolderContents(parentId: number | null, isInit = false) {
  folderLoading.value = true
  folderParentId.value = parentId
  try {
    let url = `/s/${token}/browse`
    const ps: string[] = []
    if (parentId !== null) ps.push(`parentId=${parentId}`)
    if (password.value) ps.push(`password=${encodeURIComponent(password.value)}`)
    if (ps.length) url += '?' + ps.join('&')
    const data: any = await apiClient.get(url)
    folderItems.value = data.items || []
    if (isInit) {
      folderBreadcrumbs.value = [{ id: data.parentId, name: data.folderName || fileInfo.value?.fileName || '' }]
    }
  } catch { folderItems.value = [] }
  finally { folderLoading.value = false }
}

function enterFolder(item: BrowseItem) {
  folderBreadcrumbs.value.push({ id: item.id, name: item.name })
  loadFolderContents(item.id)
}

function navBreadcrumb(idx: number) {
  folderBreadcrumbs.value = folderBreadcrumbs.value.slice(0, idx + 1)
  loadFolderContents(folderBreadcrumbs.value[idx].id)
}

function folderIcon(item: BrowseItem): string {
  if (item.isDir) return '📁'; const m = item.mimeType || ''
  if (m.startsWith('image/')) return '🖼️'; if (m.startsWith('video/')) return '🎬'
  if (m.startsWith('audio/')) return '🎵'; if (m === 'application/pdf') return '📄'
  if (/zip|rar|tar/.test(m)) return '📦'; return '📃'
}

onMounted(() => loadShare())
</script>

<template>
  <div class="scene">
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>

    <div class="wrap" :class="{ 'wrap-wide': playing || (fileInfo?.isDir && !playing) }">

      <!-- 加载 -->
      <div v-if="loading" class="card"><div class="loader-dots"><span></span><span></span><span></span></div></div>

      <!-- 错误 -->
      <div v-else-if="error && !needPassword" class="card card-center">
        <div class="status-ring status-ring-err">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </div>
        <h3 class="heading">无法访问</h3><p class="desc">{{ error }}</p>
      </div>

      <!-- 密码输入 -->
      <div v-else-if="needPassword" class="card card-center">
        <div class="status-ring">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        </div>
        <h3 class="heading">需要密码</h3><p class="desc">此内容已加密，请输入提取密码</p>
        <div class="pw-row">
          <input v-model="password" type="password" placeholder="提取密码" class="pw-inp" :class="{ err: error }" autofocus @keyup.enter="loadShare(password)" />
          <button class="pw-submit" @click="loadShare(password)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>
        <p v-if="error" class="pw-err">{{ error }}</p>
      </div>

      <!-- ====== 预览器（单文件或文件夹中的子文件） ====== -->
      <div v-else-if="playing && (!fileInfo?.isDir || previewItem)" class="player-card">
        <div class="player-bar">
          <div class="player-meta">
            <span class="player-type-tag">{{ fileTypeLabel(previewItem?.name || fileInfo?.fileName || '', false) }}</span>
            <span class="player-fn">{{ previewItem?.name || fileInfo?.fileName }}</span>
          </div>
          <button class="player-exit" @click="playing = false" title="返回">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <video v-if="isVideo(previewItem?.name || fileInfo?.fileName || '')" :src="streamUrl" controls controlsList="nodownload" class="vid" autoplay @contextmenu.prevent />
        <div v-else-if="isAudio(previewItem?.name || fileInfo?.fileName || '')" class="audio-block">
          <div class="audio-glow"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg></div>
          <p class="audio-fn">{{ previewItem?.name || fileInfo?.fileName }}</p>
          <audio :src="streamUrl" controls controlsList="nodownload" class="audio-el" autoplay @contextmenu.prevent />
        </div>
        <div v-else-if="isImage(previewItem?.name || fileInfo?.fileName || '')" class="img-block">
          <img :src="streamUrl" :alt="fileInfo?.fileName" class="img-preview" @contextmenu.prevent />
        </div>
        <iframe v-else-if="isPdf(previewItem?.name || fileInfo?.fileName || '')" :src="streamUrl" class="pdf-frame" />
        <div v-else-if="isText(previewItem?.name || fileInfo?.fileName || '')" class="text-block">
          <div v-if="textLoading" class="loader-dots"><span></span><span></span><span></span></div>
          <pre v-else class="text-content">{{ textContent }}</pre>
        </div>
      </div>

      <!-- ====== 文件夹浏览器 ====== -->
      <div v-else-if="fileInfo?.isDir && !playing" class="card folder-card">
        <!-- 头 -->
        <div class="folder-head">
          <div class="folder-head-left">
            <div class="icon-puck icon-puck-sm" style="margin-bottom:0;width:48px;height:48px;border-radius:14px;flex-shrink:0">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            </div>
            <div>
              <h3 class="heading" style="margin:0">{{ fileInfo.fileName }}</h3>
              <p class="folder-sub">{{ folderItems.length }} 个项目{{ fileInfo.allowDownload ? ' · 可下载' : ' · 仅预览' }}</p>
            </div>
          </div>
        </div>
        <!-- 面包屑 -->
        <div class="folder-bc">
          <span v-for="(bc, i) in folderBreadcrumbs" :key="i">
            <a v-if="i < folderBreadcrumbs.length - 1" class="bc-link" @click="navBreadcrumb(i)">{{ bc.name }}</a>
            <span v-else class="bc-cur">{{ bc.name }}</span>
            <span v-if="i < folderBreadcrumbs.length - 1" class="bc-sep"> / </span>
          </span>
        </div>
        <!-- 列表 -->
        <div class="folder-list">
          <div v-if="folderLoading" class="folder-state"><div class="loader-dots"><span></span><span></span><span></span></div></div>
          <div v-else-if="!folderItems.length" class="folder-state">此目录为空</div>
          <div v-for="item in folderItems" :key="item.id" class="folder-row">
            <span class="fi">{{ folderIcon(item) }}</span>
            <span class="fn">{{ item.name }}</span>
            <span class="fs">{{ item.isDir ? '' : formatSize(item.size) }}</span>
            <span class="fa">
              <button v-if="item.isDir" class="fbtn" @click="enterFolder(item)">📂 打开</button>
              <span v-else-if="isPreviewable(item.name)" class="fa-actions">
                <button v-if="fileInfo.allowDownload" class="fbtn" @click="downloadFile(item.id)">⬇</button>
                <button class="fbtn fbtn-play" @click="startPlay(item)">▶</button>
              </span>
              <button v-else-if="fileInfo.allowDownload" class="fbtn" @click="downloadFile(item.id)">⬇ 下载</button>
              <span v-else class="fno">—</span>
            </span>
          </div>
        </div>
      </div>

      <!-- ====== 单文件信息卡 ====== -->
      <div v-else-if="fileInfo && !fileInfo.isDir && !playing" class="card card-center">
        <div class="icon-puck" :class="{
          'icon-video': isVideo(fileInfo.fileName), 'icon-audio': isAudio(fileInfo.fileName),
          'icon-image': isImage(fileInfo.fileName), 'icon-pdf': isPdf(fileInfo.fileName),
          'icon-text': isText(fileInfo.fileName), 'icon-office': isOffice(fileInfo.fileName),
        }">
          <svg v-if="isVideo(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
          <svg v-else-if="isAudio(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          <svg v-else-if="isImage(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
          <svg v-else-if="isPdf(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          <svg v-else-if="isOffice(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><rect x="8" y="12" width="8" height="6" rx="1"/></svg>
          <svg v-else-if="isText(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          <svg v-else width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <h3 class="heading">{{ fileInfo.fileName }}</h3>
        <p class="desc">{{ formatSize(fileInfo.fileSize) }} · {{ fileTypeLabel(fileInfo.fileName, false) }}</p>
        <div class="btn-stack">
          <template v-if="isPreviewable(fileInfo.fileName) && fileInfo.allowDownload">
            <button class="btn btn-outline" @click="downloadFile()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              下载文件
            </button>
            <button class="btn btn-fill" @click="startPlay()">{{ previewActionLabel(fileInfo.fileName) }}</button>
          </template>
          <button v-else-if="isPreviewable(fileInfo.fileName)" class="btn btn-fill" @click="startPlay()">{{ previewActionLabel(fileInfo.fileName) }}</button>
          <button v-else-if="fileInfo.allowDownload" class="btn btn-fill" @click="downloadFile()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            下载文件
          </button>
          <div v-else class="notice"><p>此文件暂不支持预览或下载</p></div>
        </div>
      </div>

      <div class="brand-footer">
        <span class="brand-footer-icon"><img src="/logo/logo.svg" alt="" class="brand-footer-logo" /></span>
        臻橙云盘
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ═════════ 场景 ═════════ */
.scene { min-height:100vh;display:flex;align-items:center;justify-content:center;background:#faf9f7;position:relative;overflow:hidden;padding:24px }
.bg-orb { position:fixed;border-radius:50%;filter:blur(120px);opacity:.35;pointer-events:none;z-index:0 }
.bg-orb-1 { width:500px;height:500px;background:#ede9fe;top:-200px;right:-150px }
.bg-orb-2 { width:400px;height:400px;background:#fef3c7;bottom:-180px;left:-120px }

/* ═════════ LAYOUT ═════════ */
.wrap { position:relative;z-index:1;width:100%;max-width:420px;display:flex;flex-direction:column;align-items:center;gap:20px;animation:riseIn .5s cubic-bezier(.16,1,.3,1) both;transition:max-width .3s ease }
.wrap-wide { max-width:960px }
@keyframes riseIn { from { opacity:0;transform:translateY(16px) } to { opacity:1;transform:translateY(0) } }

/* ═════════ CARD ═════════ */
.card { width:100%;background:#fff;border-radius:24px;padding:40px 32px;box-shadow:0 1px 2px rgba(0,0,0,.04),0 8px 32px rgba(0,0,0,.06);position:relative }
.card-center { display:flex;flex-direction:column;align-items:center;text-align:center }
.loader-dots { display:flex;gap:8px;justify-content:center;padding:40px 0 }
.loader-dots span { width:8px;height:8px;border-radius:50%;background:#d4d4d8;animation:dotPulse 1.2s ease-in-out infinite }
.loader-dots span:nth-child(2) { animation-delay:.15s }
.loader-dots span:nth-child(3) { animation-delay:.3s }
@keyframes dotPulse { 0%,80%,100%{transform:scale(.6);opacity:.4} 40%{transform:scale(1);opacity:1} }
.heading { font-size:18px;font-weight:650;color:#18181b;margin:0 0 4px;word-break:break-all;line-height:1.4 }
.desc { font-size:13px;color:#a1a1aa;margin:0 0 28px;line-height:1.5 }

/* ═════════ 状态环 ═════════ */
.status-ring { width:64px;height:64px;border-radius:50%;background:#f4f4f5;display:flex;align-items:center;justify-content:center;margin-bottom:20px;color:#71717a }
.status-ring-err { background:#fef2f2;color:#ef4444 }

/* ═════════ 密码 ═════════ */
.pw-row { width:100%;display:flex;gap:0;margin-bottom:4px }
.pw-inp { flex:1;height:48px;padding:0 18px;border:1.5px solid #e4e4e7;border-right:none;border-radius:14px 0 0 14px;font-size:15px;color:#18181b;outline:none;background:#fafafa;transition:border-color .2s,background .2s }
.pw-inp:focus { border-color:#6366f1;background:#fff }
.pw-inp.err { border-color:#ef4444 }
.pw-submit { width:52px;height:48px;border:1.5px solid #6366f1;border-radius:0 14px 14px 0;background:#6366f1;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:background .15s }
.pw-submit:hover { background:#4f46e5 }
.pw-err { font-size:12px;color:#ef4444;margin:6px 0 0 }

/* ═════════ 图标 ═════════ */
.icon-puck { width:96px;height:96px;border-radius:22px;display:flex;align-items:center;justify-content:center;margin-bottom:20px;background:#f4f4f5;color:#71717a }
.icon-video{background:#ede9fe;color:#7c3aed}.icon-audio{background:#fef3c7;color:#d97706}.icon-image{background:#e0f2fe;color:#0284c7}.icon-pdf{background:#fee2e2;color:#dc2626}.icon-text{background:#f0fdf4;color:#16a34a}.icon-office{background:#fff7ed;color:#ea580c}

/* ═════════ BUTTONS ═════════ */
.btn-stack { width:100%;display:flex;flex-direction:column;gap:10px }
.btn { width:100%;height:48px;border-radius:14px;font-size:14px;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;border:none;transition:all .15s }
.btn-fill { background:#18181b;color:#fff }
.btn-fill:hover { background:#27272a }
.btn-outline { background:#fff;color:#52525b;border:1.5px solid #e4e4e7 }
.btn-outline:hover { background:#fafafa;border-color:#d4d4d8 }
.notice { padding:16px;background:#fafafa;border-radius:14px }
.notice p { margin:0;font-size:13px;color:#a1a1aa }

/* ═════════ PLAYER ═════════ */
.player-card { width:100%;max-width:960px;background:#18181b;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.2) }
.player-bar { display:flex;align-items:center;justify-content:space-between;padding:14px 20px;gap:12px }
.player-meta { display:flex;align-items:center;gap:10px;min-width:0 }
.player-type-tag { font-size:11px;font-weight:600;color:#a1a1aa;letter-spacing:.06em;background:#27272a;padding:3px 8px;border-radius:6px;flex-shrink:0 }
.player-fn { font-size:13px;color:#e4e4e7;overflow:hidden;text-overflow:ellipsis;white-space:nowrap }
.player-exit { width:32px;height:32px;border:none;background:#27272a;border-radius:8px;cursor:pointer;color:#a1a1aa;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s }
.player-exit:hover { background:#3f3f46;color:#fff }
.vid{width:100%;display:block;max-height:640px}
.audio-block{padding:40px 20px;display:flex;flex-direction:column;align-items:center;gap:20px}.audio-glow{width:100px;height:100px;border-radius:50%;background:#27272a;display:flex;align-items:center;justify-content:center;color:#a78bfa}.audio-fn{font-size:14px;color:#d4d4d8;margin:0;max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.audio-el{width:100%;max-width:320px}
.img-block{padding:0;background:#0f172a;display:flex;align-items:center;justify-content:center}.img-preview{width:100%;max-height:640px;object-fit:contain;display:block}
.pdf-frame{width:100%;height:640px;border:none}
.text-block{padding:0;max-height:640px;overflow:auto}.text-content{margin:0;padding:24px;font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:13px;line-height:1.7;color:#e2e8f0;white-space:pre-wrap;word-break:break-all;background:#0f172a;min-height:200px}

/* ═════════ FOLDER BROWSER ═════════ */
.folder-card { padding:28px 0 0; overflow:hidden }
.folder-head { padding:0 28px 20px; display:flex;align-items:center;justify-content:space-between }
.folder-head-left { display:flex;align-items:center;gap:14px }
.folder-sub { margin:2px 0 0;font-size:12px;color:#a1a1aa }
.folder-bc { padding:0 28px 12px;font-size:12px;color:#a1a1aa }
.bc-link{color:#6366f1;cursor:pointer;text-decoration:none}.bc-link:hover{text-decoration:underline}
.bc-cur{color:#18181b;font-weight:500}.bc-sep{margin:0 4px;color:#d4d4d8}
.folder-list { border-top:1px solid #f1f5f9 }
.folder-row { display:flex;align-items:center;gap:10px;padding:10px 28px;border-bottom:1px solid #f1f5f9;cursor:default;transition:background .1s }
.folder-row:hover { background:#fafafa }
.folder-row .fi { font-size:20px;flex-shrink:0;width:28px;text-align:center }
.folder-row .fn { flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px;color:#18181b;font-weight:500 }
.folder-row .fs { font-size:12px;color:#a1a1aa;min-width:60px;text-align:right }
.folder-row .fa { min-width:60px;text-align:right }
.fa-actions { display:flex;gap:4px }
.fbtn { height:28px;padding:0 10px;border:1px solid #e4e4e7;border-radius:7px;background:#fff;font-size:12px;color:#52525b;cursor:pointer;transition:all .12s;white-space:nowrap;display:inline-flex;align-items:center;gap:3px }
.fbtn:hover { border-color:#6366f1;color:#6366f1;background:rgba(99,102,241,.04) }
.fbtn-play { border-color:#6366f1;color:#6366f1;background:rgba(99,102,241,.04) }
.fbtn-play:hover { background:rgba(99,102,241,.08) }
.fno { font-size:12px;color:#d4d4d8 }
.folder-state { padding:40px;text-align:center;color:#a1a1aa;font-size:13px }

/* ═════════ BRAND ═════════ */
.brand-footer { display:flex;align-items:center;gap:8px;font-size:13px;font-weight:500;color:#71717a;letter-spacing:.04em }
.brand-footer-icon { display:flex;align-items:center;justify-content:center;width:22px;height:22px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:5px;padding:3px;box-sizing:border-box;flex-shrink:0 }
.brand-footer-logo { width:100%;height:100%;object-fit:contain;filter:brightness(0) invert(1) }

/* ═════════ MOBILE ═════════ */
@media (max-width:480px) {
  .scene{padding:16px;align-items:flex-start;padding-top:64px}
  .card{padding:28px 20px;border-radius:20px}.folder-card{padding:20px 0 0}
  .heading{font-size:16px}.btn{height:50px;font-size:15px;border-radius:16px}
  .pw-inp,.pw-submit{height:50px}.pw-inp{font-size:16px}
  .icon-puck{width:80px;height:80px;border-radius:18px}.icon-puck svg{width:32px;height:32px}
  .vid{max-height:280px}.img-preview{max-height:360px}.pdf-frame{height:420px}.text-content{font-size:11px;padding:16px}
  .player-card{max-width:100%;border-radius:14px}.audio-el{max-width:100%}
  .folder-head,.folder-bc,.folder-row{padding-left:16px;padding-right:16px}
  .folder-row .fs{display:none}
}
</style>
