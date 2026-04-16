<script setup lang="ts">
const route = useRoute()
const token = route.params.token as string
const { $post } = useApi()

const loading = ref(true)
const needPassword = ref(false)
const password = ref('')
const error = ref('')

const fileInfo = ref<{
  fileName: string
  fileSize: number
  isDir: boolean
} | null>(null)

async function loadShare(pwd?: string) {
  loading.value = true
  error.value = ''
  try {
    const data = await $post<{
      fileName?: string
      fileSize?: number
      isDir?: boolean
      hasPassword?: boolean
      needPassword?: boolean
    }>(`/s/${token}`, pwd ? { password: pwd } : undefined)

    if (data.needPassword) {
      needPassword.value = true
      error.value = pwd ? '密码错误' : ''
    } else {
      fileInfo.value = {
        fileName: data.fileName!,
        fileSize: data.fileSize!,
        isDir: data.isDir!,
      }
      needPassword.value = false
    }
  } catch (e: any) {
    const msg = e?.data?.detail || e?.message || '访问失败'
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
    const data = await $post<{ url: string; name: string }>(
      `/s/${token}/download`,
      password.value ? { password: password.value } : undefined,
    )
    window.open(data.url, '_blank')
  } catch (e: any) {
    error.value = e?.data?.detail || e?.message || '下载失败'
  }
}

function formatSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0; let s = bytes
  while (s >= 1024 && i < units.length - 1) { s /= 1024; i++ }
  return `${s.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

function getIcon(name: string, isDir: boolean): string {
  if (isDir) return '📁'
  const ext = name.split('.').pop()?.toLowerCase() || ''
  const map: Record<string, string> = {
    jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️', webp: '🖼️', svg: '🖼️',
    mp4: '🎬', mov: '🎬', avi: '🎬', mkv: '🎬',
    mp3: '🎵', wav: '🎵', flac: '🎵',
    pdf: '📄', doc: '📝', docx: '📝', xls: '📊', xlsx: '📊', ppt: '📊', pptx: '📊',
    zip: '📦', rar: '📦', '7z': '📦', tar: '📦', gz: '📦',
  }
  return map[ext] || '📃'
}

useHead({ title: '分享文件 — 青空' })

loadShare()
</script>

<template>
  <div class="share-page">
    <div class="share-card">
      <div class="share-brand">
        <span class="brand-icon">◈</span>
        <span class="brand-name">青空云盘</span>
      </div>

      <div v-if="loading" class="share-loading">加载中...</div>

      <div v-else-if="error && !needPassword" class="share-error">
        <div class="error-icon">⚠️</div>
        <div class="error-text">{{ error }}</div>
        <NuxtLink to="/" class="back-home">返回首页</NuxtLink>
      </div>

      <div v-else-if="needPassword" class="share-password">
        <div class="pw-icon">🔒</div>
        <div class="pw-title">该分享需要密码</div>
        <div v-if="error" class="pw-error">{{ error }}</div>
        <input
          v-model="password"
          type="password"
          placeholder="请输入提取密码"
          class="pw-input"
          @keyup.enter="loadShare(password)"
        />
        <button class="pw-btn" @click="loadShare(password)">验证</button>
      </div>

      <div v-else-if="fileInfo" class="share-info">
        <div class="file-icon">{{ getIcon(fileInfo.fileName, fileInfo.isDir) }}</div>
        <div class="file-name">{{ fileInfo.fileName }}</div>
        <div class="file-size">{{ formatSize(fileInfo.fileSize) }}</div>
        <button v-if="!fileInfo.isDir" class="download-btn" @click="downloadFile">
          ⬇ 下载文件
        </button>
        <div v-else class="dir-hint">文件夹暂不支持直接下载</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.share-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  padding: 20px;
}

.share-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.share-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
}

.brand-icon {
  font-size: 24px;
  color: var(--color-primary);
}

.brand-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-heading);
}

.share-loading {
  padding: 40px 0;
  color: var(--color-text-light);
  font-size: 14px;
}

.share-error { padding: 20px 0; }
.error-icon { font-size: 40px; margin-bottom: 12px; }
.error-text { font-size: 14px; color: #ef4444; margin-bottom: 16px; }
.back-home {
  display: inline-block;
  padding: 8px 20px;
  background: var(--color-primary);
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
}

.share-password { padding: 20px 0; }
.pw-icon { font-size: 40px; margin-bottom: 12px; }
.pw-title { font-size: 16px; font-weight: 500; color: var(--color-heading); margin-bottom: 16px; }
.pw-error { font-size: 13px; color: #ef4444; margin-bottom: 8px; }
.pw-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 12px;
  background: var(--color-surface);
  color: var(--color-text);
  text-align: center;
}
.pw-input:focus { outline: none; border-color: var(--color-primary); }
.pw-btn {
  width: 100%;
  padding: 10px;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}
.pw-btn:hover { opacity: 0.9; }

.share-info { padding: 20px 0; }
.file-icon { font-size: 56px; margin-bottom: 16px; }
.file-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 6px;
  word-break: break-all;
}
.file-size {
  font-size: 13px;
  color: var(--color-text-light);
  margin-bottom: 24px;
}
.download-btn {
  width: 100%;
  padding: 12px;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  font-weight: 500;
}
.download-btn:hover { opacity: 0.9; }
.dir-hint {
  font-size: 13px;
  color: var(--color-text-light);
  padding: 12px;
  background: var(--color-bg);
  border-radius: 8px;
}
</style>
