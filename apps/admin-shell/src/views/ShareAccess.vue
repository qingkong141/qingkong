<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiClient } from '@qingkong/shared-api'

const route = useRoute()
const token = route.params.token as string

const loading = ref(true)
const needPassword = ref(false)
const password = ref('')
const error = ref('')
const fileInfo = ref<{ fileName: string; fileSize: number; isDir: boolean } | null>(null)

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
    jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️', webp: '🖼️',
    mp4: '🎬', mov: '🎬', mp3: '🎵', wav: '🎵',
    pdf: '📄', zip: '📦', rar: '📦',
  }
  return map[ext] || '📃'
}

onMounted(() => loadShare())
</script>

<template>
  <div class="share-page">
    <div class="share-card">
      <div class="share-brand">
        <span class="brand-icon">◈</span>
        <span class="brand-name">青空云盘</span>
      </div>

      <div v-if="loading" class="share-state">加载中...</div>

      <div v-else-if="error && !needPassword" class="share-state">
        <div class="state-icon">⚠️</div>
        <div class="state-error">{{ error }}</div>
      </div>

      <div v-else-if="needPassword" class="pw-section">
        <div class="state-icon">🔒</div>
        <div class="pw-title">该分享需要密码</div>
        <div v-if="error" class="pw-error">{{ error }}</div>
        <input
          v-model="password" type="password" placeholder="请输入提取密码"
          class="pw-input" @keyup.enter="loadShare(password)"
        />
        <button class="pw-btn" @click="loadShare(password)">验证</button>
      </div>

      <div v-else-if="fileInfo" class="file-section">
        <div class="file-icon">{{ getIcon(fileInfo.fileName, fileInfo.isDir) }}</div>
        <div class="file-name">{{ fileInfo.fileName }}</div>
        <div class="file-size">{{ formatSize(fileInfo.fileSize) }}</div>
        <button v-if="!fileInfo.isDir" class="dl-btn" @click="downloadFile">⬇ 下载文件</button>
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
  background: var(--bg-page, #f9fafb);
}

.share-card {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 14px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,.08);
}

.share-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
}
.brand-icon { font-size: 24px; color: var(--accent, #6366f1); }
.brand-name { font-size: 17px; font-weight: 700; color: var(--text-1, #111827); }

.share-state { padding: 40px 0; color: var(--text-3, #9ca3af); font-size: 13px; }
.state-icon { font-size: 40px; margin-bottom: 12px; }
.state-error { font-size: 13px; color: #ef4444; }

.pw-section { padding: 20px 0; }
.pw-title { font-size: 15px; font-weight: 600; color: var(--text-1, #111827); margin-bottom: 16px; }
.pw-error { font-size: 12px; color: #ef4444; margin-bottom: 8px; }
.pw-input {
  width: 100%; height: 38px; padding: 0 14px;
  border: 1px solid var(--border, #e5e7eb); border-radius: 7px;
  font-size: 13px; margin-bottom: 12px;
  background: var(--bg-surface, #fff); color: var(--text-1, #111827);
  text-align: center; box-sizing: border-box; outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.pw-input:focus { border-color: var(--accent, #6366f1); box-shadow: 0 0 0 3px rgba(99,102,241,.1); }
.pw-btn {
  width: 100%; height: 38px; background: var(--accent, #6366f1); color: #fff;
  border: none; border-radius: 8px; font-size: 13px; font-weight: 500;
  cursor: pointer; transition: opacity 0.15s;
}
.pw-btn:hover { opacity: 0.88; }

.file-section { padding: 20px 0; }
.file-icon { font-size: 48px; margin-bottom: 14px; }
.file-name {
  font-size: 15px; font-weight: 600; color: var(--text-1, #111827);
  margin-bottom: 4px; word-break: break-all;
}
.file-size { font-size: 12px; color: var(--text-3, #9ca3af); margin-bottom: 24px; }
.dl-btn {
  width: 100%; height: 40px; background: var(--accent, #6366f1); color: #fff;
  border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 500;
  transition: opacity 0.15s;
}
.dl-btn:hover { opacity: 0.88; }
.dir-hint {
  font-size: 12px; color: var(--text-3, #9ca3af); padding: 12px;
  background: var(--bg-page, #f9fafb); border-radius: 8px;
  border: 1px solid var(--border, #e5e7eb);
}
</style>
