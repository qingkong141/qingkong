<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiClient } from '@qingkong/shared-api'

const route = useRoute()
const token = route.params.token as string

const loading = ref(true)
const needPassword = ref(false)
const password = ref('')
const error = ref('')
const fileInfo = ref<{ fileName: string; fileSize: number; isDir: boolean; allowDownload: boolean } | null>(null)
const playing = ref(false)
const textContent = ref('')
const textLoading = ref(false)

const streamUrl = computed(() => {
  const base = `/qingkong/s/${token}/stream`
  return password.value ? `${base}?password=${encodeURIComponent(password.value)}` : base
})

function isVideo(name: string): boolean {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  return ['mp4', 'mov', 'webm', 'mkv'].includes(ext)
}

function isAudio(name: string): boolean {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  return ['mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac'].includes(ext)
}

function isImage(name: string): boolean {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico'].includes(ext)
}

function isPdf(name: string): boolean {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  return ext === 'pdf'
}

function isText(name: string): boolean {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  return ['txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'ts', 'jsx', 'tsx', 'vue', 'py', 'java', 'go', 'rs', 'sh', 'yml', 'yaml', 'toml', 'ini', 'cfg', 'log', 'sql', 'env'].includes(ext)
}

function isOffice(name: string): boolean {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  return ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].includes(ext)
}

function isPlayable(name: string): boolean {
  return isVideo(name) || isAudio(name)
}

function isPreviewable(name: string): boolean {
  return isVideo(name) || isAudio(name) || isImage(name) || isPdf(name) || isText(name)
}

function fileExt(name: string): string {
  return name.split('.').pop()?.toUpperCase() || ''
}

async function loadShare(pwd?: string) {
  loading.value = true
  error.value = ''
  try {
    const data: any = await apiClient.post(`/s/${token}`, pwd ? { password: pwd } : {})
    if (data.needPassword) {
      needPassword.value = true
      error.value = pwd ? '密码错误' : ''
    } else {
      fileInfo.value = {
        fileName: data.fileName,
        fileSize: data.fileSize,
        isDir: data.isDir,
        allowDownload: data.allowDownload !== false,
      }
      needPassword.value = false
    }
  } catch (e: any) {
    const msg = e?.message || '访问失败'
    if (msg.includes('密码')) {
      needPassword.value = true
      error.value = pwd ? '密码错误' : ''
    } else {
      error.value = msg
    }
  } finally {
    loading.value = false
  }
}

async function downloadFile() {
  error.value = ''
  try {
    const data: any = await apiClient.post(
      `/s/${token}/download`,
      password.value ? { password: password.value } : {},
    )
    window.open(data.url, '_blank')
  } catch (e: any) {
    error.value = e?.message || '下载失败'
  }
}

function startPlay() {
  error.value = ''
  playing.value = true
  // 文本文件需要额外 fetch
  if (fileInfo.value && isText(fileInfo.value.fileName)) {
    textLoading.value = true
    textContent.value = ''
    fetch(streamUrl.value)
      .then(r => r.text())
      .then(t => { textContent.value = t })
      .catch(() => { textContent.value = '无法加载文件内容' })
      .finally(() => { textLoading.value = false })
  }
}

function previewActionLabel(name: string): string {
  if (isVideo(name)) return '播放视频'
  if (isAudio(name)) return '播放音频'
  if (isImage(name)) return '查看图片'
  if (isPdf(name)) return '查看文档'
  if (isText(name)) return '查看内容'
  return ''
}

function formatSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0; let s = bytes
  while (s >= 1024 && i < units.length - 1) { s /= 1024; i++ }
  return `${s.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

function fileTypeLabel(name: string, isDir: boolean): string {
  if (isDir) return '文件夹'
  if (isVideo(name)) return '视频文件'
  if (isAudio(name)) return '音频文件'
  if (isImage(name)) return '图片'
  if (isPdf(name)) return 'PDF 文档'
  if (isOffice(name)) return 'Office 文档'
  if (isText(name)) return '文本文件'
  const ext = name.split('.').pop()?.toLowerCase() || ''
  const map: Record<string, string> = { zip: '压缩包', rar: '压缩包' }
  return map[ext] || `${ext.toUpperCase()} 文件`
}

onMounted(() => loadShare())
</script>

<template>
  <div class="scene">
    <!-- 背景装饰 -->
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>

    <!-- 内容区 -->
    <div class="wrap" :class="{ 'wrap-wide': playing }">

      <!-- ====== 加载态 ====== -->
      <div v-if="loading" class="card">
        <div class="loader-dots">
          <span></span><span></span><span></span>
        </div>
      </div>

      <!-- ====== 错误态 ====== -->
      <div v-else-if="error && !needPassword" class="card card-center">
        <div class="status-ring status-ring-err">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </div>
        <h3 class="heading">无法访问</h3>
        <p class="desc">{{ error }}</p>
      </div>

      <!-- ====== 密码输入 ====== -->
      <div v-else-if="needPassword" class="card card-center">
        <div class="status-ring">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </div>
        <h3 class="heading">需要密码</h3>
        <p class="desc">此内容已加密，请输入提取密码</p>
        <div class="pw-row">
          <input
            v-model="password"
            type="password"
            placeholder="提取密码"
            class="pw-inp"
            :class="{ err: error }"
            autofocus
            @keyup.enter="loadShare(password)"
          />
          <button class="pw-submit" @click="loadShare(password)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
        </div>
        <p v-if="error" class="pw-err">{{ error }}</p>
      </div>

      <!-- ====== 预览器 ====== -->
      <div v-else-if="playing && fileInfo" class="player-card">
        <!-- 顶栏 -->
        <div class="player-bar">
          <div class="player-meta">
            <span class="player-type-tag">{{ fileTypeLabel(fileInfo.fileName, fileInfo.isDir) }}</span>
            <span class="player-fn">{{ fileInfo.fileName }}</span>
          </div>
          <button class="player-exit" @click="playing = false" title="返回">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- 视频 -->
        <video v-if="isVideo(fileInfo.fileName)" :src="streamUrl" controls controlsList="nodownload" class="vid" autoplay @contextmenu.prevent />

        <!-- 音频 -->
        <div v-else-if="isAudio(fileInfo.fileName)" class="audio-block">
          <div class="audio-glow">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
            </svg>
          </div>
          <p class="audio-fn">{{ fileInfo.fileName }}</p>
          <audio :src="streamUrl" controls controlsList="nodownload" class="audio-el" autoplay @contextmenu.prevent />
        </div>

        <!-- 图片 -->
        <div v-else-if="isImage(fileInfo.fileName)" class="img-block">
          <img :src="streamUrl" :alt="fileInfo.fileName" class="img-preview" @contextmenu.prevent />
        </div>

        <!-- PDF -->
        <iframe v-else-if="isPdf(fileInfo.fileName)" :src="streamUrl" class="pdf-frame" />

        <!-- 文本 -->
        <div v-else-if="isText(fileInfo.fileName)" class="text-block">
          <div v-if="textLoading" class="loader-dots"><span></span><span></span><span></span></div>
          <pre v-else class="text-content">{{ textContent }}</pre>
        </div>
      </div>

      <!-- ====== 文件信息卡 ====== -->
      <div v-else-if="fileInfo && !playing" class="card card-center">
        <!-- 文件图标 -->
        <div class="icon-puck" :class="{
          'icon-video': isVideo(fileInfo.fileName),
          'icon-audio': isAudio(fileInfo.fileName),
          'icon-image': isImage(fileInfo.fileName),
          'icon-pdf': isPdf(fileInfo.fileName),
          'icon-text': isText(fileInfo.fileName),
          'icon-office': isOffice(fileInfo.fileName),
        }">
          <!-- 视频图标 -->
          <svg v-if="isVideo(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
          </svg>
          <!-- 音频图标 -->
          <svg v-else-if="isAudio(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
          </svg>
          <!-- 图片图标 -->
          <svg v-else-if="isImage(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
          </svg>
          <!-- PDF 图标 -->
          <svg v-else-if="isPdf(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <!-- Office 图标 -->
          <svg v-else-if="isOffice(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><rect x="8" y="12" width="8" height="6" rx="1"/>
          </svg>
          <!-- 文本图标 -->
          <svg v-else-if="isText(fileInfo.fileName)" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <!-- 文件夹图标 -->
          <svg v-else-if="fileInfo.isDir" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <!-- 通用文件图标 -->
          <svg v-else width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
          </svg>
        </div>

        <!-- 文件名 -->
        <h3 class="heading">{{ fileInfo.fileName }}</h3>
        <p class="desc">{{ formatSize(fileInfo.fileSize) }} · {{ fileTypeLabel(fileInfo.fileName, fileInfo.isDir) }}</p>

        <!-- 操作按钮 -->
        <div class="btn-stack">
          <!-- 可预览 + 可下载：两个按钮 -->
          <template v-if="isPreviewable(fileInfo.fileName) && fileInfo.allowDownload">
            <button class="btn btn-outline" @click="downloadFile">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              下载文件
            </button>
            <button class="btn btn-fill" @click="startPlay">{{ previewActionLabel(fileInfo.fileName) }}</button>
          </template>
          <!-- 可预览、不可下载 -->
          <button v-else-if="isPreviewable(fileInfo.fileName)" class="btn btn-fill" @click="startPlay">{{ previewActionLabel(fileInfo.fileName) }}</button>
          <!-- 可下载、不可预览 -->
          <button v-else-if="fileInfo.allowDownload" class="btn btn-fill" @click="downloadFile">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            下载文件
          </button>
          <!-- Office：不可预览但可下载时显示提示 -->
          <div v-else-if="isOffice(fileInfo.fileName) && !fileInfo.allowDownload" class="notice">
            <p>Office 文档暂不支持在线预览</p>
          </div>
          <!-- 其他不可预览、不可下载 -->
          <div v-else class="notice">
            <p>此文件暂不支持预览或下载</p>
          </div>
        </div>
      </div>

      <!-- 底部署名 -->
      <p class="brand">臻橙云盘</p>
    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════
   SCENE
   ═══════════════════════════════════════════════ */
.scene {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #faf9f7;
  position: relative;
  overflow: hidden;
  padding: 24px;
}

/* 背景光晕 */
.bg-orb {
  position: fixed;
  border-radius: 50%;
  filter: blur(120px);
  opacity: .35;
  pointer-events: none;
  z-index: 0;
}
.bg-orb-1 {
  width: 500px; height: 500px;
  background: #ede9fe;
  top: -200px; right: -150px;
}
.bg-orb-2 {
  width: 400px; height: 400px;
  background: #fef3c7;
  bottom: -180px; left: -120px;
}

/* ═══════════════════════════════════════════════
   LAYOUT
   ═══════════════════════════════════════════════ */
.wrap {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  animation: riseIn .5s cubic-bezier(.16,1,.3,1) both;
  transition: max-width .3s ease;
}
.wrap-wide { max-width: 960px; }

@keyframes riseIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════════════════════════════════
   CARD
   ═══════════════════════════════════════════════ */
.card {
  width: 100%;
  background: #fff;
  border-radius: 24px;
  padding: 40px 32px;
  box-shadow:
    0 1px 2px rgba(0,0,0,.04),
    0 8px 32px rgba(0,0,0,.06);
  position: relative;
}

.card-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* ═══════════════════════════════════════════════
   LOADER
   ═══════════════════════════════════════════════ */
.loader-dots {
  display: flex; gap: 8px; justify-content: center; padding: 40px 0;
}
.loader-dots span {
  width: 8px; height: 8px; border-radius: 50%; background: #d4d4d8;
  animation: dotPulse 1.2s ease-in-out infinite;
}
.loader-dots span:nth-child(2) { animation-delay: .15s; }
.loader-dots span:nth-child(3) { animation-delay: .3s; }
@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(.6); opacity: .4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ═══════════════════════════════════════════════
   TYPOGRAPHY
   ═══════════════════════════════════════════════ */
.heading {
  font-size: 18px; font-weight: 650; color: #18181b; margin: 0 0 4px;
  word-break: break-all; line-height: 1.4;
}
.desc {
  font-size: 13px; color: #a1a1aa; margin: 0 0 28px; line-height: 1.5;
}

/* ═══════════════════════════════════════════════
   STATUS RING
   ═══════════════════════════════════════════════ */
.status-ring {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: #f4f4f5;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px; color: #71717a;
}
.status-ring-err { background: #fef2f2; color: #ef4444; }

/* ═══════════════════════════════════════════════
   PASSWORD
   ═══════════════════════════════════════════════ */
.pw-row {
  width: 100%; display: flex; gap: 0; margin-bottom: 4px;
}
.pw-inp {
  flex: 1; height: 48px; padding: 0 18px;
  border: 1.5px solid #e4e4e7; border-right: none; border-radius: 14px 0 0 14px;
  font-size: 15px; color: #18181b; outline: none; background: #fafafa;
  transition: border-color .2s, background .2s;
}
.pw-inp:focus { border-color: #6366f1; background: #fff; }
.pw-inp.err { border-color: #ef4444; }
.pw-submit {
  width: 52px; height: 48px; border: 1.5px solid #6366f1; border-radius: 0 14px 14px 0;
  background: #6366f1; color: #fff; cursor: pointer; display: flex;
  align-items: center; justify-content: center; flex-shrink: 0;
  transition: background .15s;
}
.pw-submit:hover { background: #4f46e5; }
.pw-err { font-size: 12px; color: #ef4444; margin: 6px 0 0; }

/* ═══════════════════════════════════════════════
   FILE ICON
   ═══════════════════════════════════════════════ */
.icon-puck {
  width: 96px; height: 96px; border-radius: 22px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px;
  background: #f4f4f5;
  color: #71717a;
  transition: transform .2s;
}
.icon-video { background: #ede9fe; color: #7c3aed; }
.icon-audio { background: #fef3c7; color: #d97706; }
.icon-image { background: #e0f2fe; color: #0284c7; }
.icon-pdf   { background: #fee2e2; color: #dc2626; }
.icon-text  { background: #f0fdf4; color: #16a34a; }
.icon-office { background: #fff7ed; color: #ea580c; }

/* ═══════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════ */
.btn-stack {
  width: 100%; display: flex; flex-direction: column; gap: 10px;
}
.btn {
  width: 100%; height: 48px; border-radius: 14px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  border: none; transition: all .15s;
}
.btn-fill {
  background: #18181b; color: #fff;
}
.btn-fill:hover {
  background: #27272a;
}
.btn-outline {
  background: #fff; color: #52525b;
  border: 1.5px solid #e4e4e7;
}
.btn-outline:hover { background: #fafafa; border-color: #d4d4d8; }

.notice {
  padding: 16px; background: #fafafa; border-radius: 14px;
}
.notice p { margin: 0; font-size: 13px; color: #a1a1aa; }

/* ═══════════════════════════════════════════════
   PLAYER
   ═══════════════════════════════════════════════ */
.player-card {
  width: 100%; max-width: 960px;
  background: #18181b; border-radius: 16px; overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,.2);
}
.player-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 20px; gap: 12px;
}
.player-meta { display: flex; align-items: center; gap: 10px; min-width: 0; }
.player-type-tag {
  font-size: 11px; font-weight: 600; color: #a1a1aa; text-transform: uppercase;
  letter-spacing: .06em; background: #27272a; padding: 3px 8px; border-radius: 6px;
  flex-shrink: 0;
}
.player-fn {
  font-size: 13px; color: #e4e4e7; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap;
}
.player-exit {
  width: 32px; height: 32px; border: none; background: #27272a;
  border-radius: 8px; cursor: pointer; color: #a1a1aa; display: flex;
  align-items: center; justify-content: center; flex-shrink: 0;
  transition: all .15s;
}
.player-exit:hover { background: #3f3f46; color: #fff; }

.vid { width: 100%; display: block; max-height: 640px; }

.audio-block {
  padding: 40px 20px; display: flex; flex-direction: column; align-items: center; gap: 20px;
}
.audio-glow {
  width: 100px; height: 100px; border-radius: 50%;
  background: #27272a; display: flex; align-items: center; justify-content: center;
  color: #a78bfa;
}
.audio-fn {
  font-size: 14px; color: #d4d4d8; margin: 0;
  max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.audio-el { width: 100%; max-width: 320px; }

/* 图片 */
.img-block { padding: 0; background: #0f172a; display: flex; align-items: center; justify-content: center; }
.img-preview { width: 100%; max-height: 640px; object-fit: contain; display: block; }

/* PDF */
.pdf-frame { width: 100%; height: 640px; border: none; }

/* 文本 */
.text-block { padding: 0; max-height: 640px; overflow: auto; }
.text-content {
  margin: 0; padding: 24px; font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px; line-height: 1.7; color: #e2e8f0; white-space: pre-wrap; word-break: break-all;
  background: #0f172a; min-height: 200px;
}

/* ═══════════════════════════════════════════════
   BRAND
   ═══════════════════════════════════════════════ */
.brand {
  font-size: 12px; color: #d4d4d8; letter-spacing: .04em; margin: 0;
}

/* ═══════════════════════════════════════════════
   MOBILE
   ═══════════════════════════════════════════════ */
@media (max-width: 480px) {
  .scene { padding: 16px; align-items: flex-start; padding-top: 64px; }
  .card { padding: 28px 20px; border-radius: 20px; }
  .heading { font-size: 16px; }
  .btn { height: 50px; font-size: 15px; border-radius: 16px; }
  .pw-inp { height: 50px; font-size: 16px; }
  .pw-submit { height: 50px; }
  .icon-puck { width: 80px; height: 80px; border-radius: 18px; }
  .icon-puck svg { width: 32px; height: 32px; }
  .vid { max-height: 280px; }
  .img-preview { max-height: 360px; }
  .pdf-frame { height: 420px; }
  .text-content { font-size: 11px; padding: 16px; }
  .player-card { max-width: 100%; border-radius: 14px; }
  .audio-el { max-width: 100%; }
}
</style>
