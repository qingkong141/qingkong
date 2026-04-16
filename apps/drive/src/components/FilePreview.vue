<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  url: string
  name: string
  mimeType: string | null
}>()

const emit = defineEmits<{ close: [] }>()

const mime = computed(() => props.mimeType || '')

const previewType = computed<'image' | 'video' | 'audio' | 'pdf' | 'text' | 'unsupported'>(() => {
  const m = mime.value
  if (m.startsWith('image/')) return 'image'
  if (m.startsWith('video/')) return 'video'
  if (m.startsWith('audio/')) return 'audio'
  if (m === 'application/pdf') return 'pdf'
  if (m.startsWith('text/') || isCodeFile(props.name)) return 'text'
  return 'unsupported'
})

const textContent = ref('')
const textLoading = ref(false)

function isCodeFile(name: string): boolean {
  const exts = ['.js', '.ts', '.json', '.py', '.html', '.css', '.md', '.yml', '.yaml', '.xml', '.sh', '.sql', '.env', '.toml', '.cfg', '.ini', '.vue', '.jsx', '.tsx']
  return exts.some(ext => name.toLowerCase().endsWith(ext))
}

watch(() => props.url, async (url) => {
  if (previewType.value === 'text' && url) {
    textLoading.value = true
    try {
      const res = await fetch(url)
      textContent.value = await res.text()
    } catch {
      textContent.value = '无法加载文件内容'
    } finally {
      textLoading.value = false
    }
  }
}, { immediate: true })

function onMaskClick(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('preview-mask')) {
    emit('close')
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="preview-mask" @click="onMaskClick">
      <div class="preview-container">
        <div class="preview-header">
          <span class="preview-name">{{ name }}</span>
          <button class="preview-close" @click="emit('close')">✕</button>
        </div>

        <div class="preview-body">
          <!-- Image -->
          <img v-if="previewType === 'image'" :src="url" :alt="name" class="preview-img" />

          <!-- Video -->
          <video v-else-if="previewType === 'video'" :src="url" controls class="preview-video" />

          <!-- Audio -->
          <div v-else-if="previewType === 'audio'" class="preview-audio-wrap">
            <div class="audio-icon">🎵</div>
            <div class="audio-name">{{ name }}</div>
            <audio :src="url" controls class="preview-audio" />
          </div>

          <!-- PDF -->
          <iframe v-else-if="previewType === 'pdf'" :src="url" class="preview-pdf" />

          <!-- Text / Code -->
          <div v-else-if="previewType === 'text'" class="preview-text-wrap">
            <div v-if="textLoading" class="text-loading">加载中...</div>
            <pre v-else class="preview-text">{{ textContent }}</pre>
          </div>

          <!-- Unsupported -->
          <div v-else class="preview-unsupported">
            <div class="unsup-icon">📎</div>
            <div>此文件类型暂不支持预览</div>
            <a :href="url" target="_blank" class="unsup-download">下载文件</a>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.preview-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; z-index: 9999;
  backdrop-filter: blur(2px);
}

.preview-container {
  background: var(--bg-surface, #fff); border-radius: 14px;
  width: 90vw; max-width: 900px; max-height: 85vh;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,.18);
}

.preview-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 20px; border-bottom: 1px solid var(--border, #e5e7eb);
}

.preview-name {
  font-size: 14px; font-weight: 600; color: var(--text-1, #111827);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.preview-close {
  background: none; border: 1px solid var(--border, #e5e7eb); font-size: 15px; cursor: pointer;
  color: var(--text-2, #6b7280); width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; transition: all 0.12s;
}
.preview-close:hover { border-color: var(--accent, #6366f1); color: var(--accent, #6366f1); background: rgba(99,102,241,.05); }

.preview-body {
  flex: 1; overflow: auto; display: flex; align-items: center; justify-content: center;
  padding: 20px; min-height: 300px;
}

.preview-img { max-width: 100%; max-height: 65vh; object-fit: contain; border-radius: 6px; }
.preview-video { max-width: 100%; max-height: 65vh; border-radius: 6px; }

.preview-audio-wrap { text-align: center; }
.audio-icon { font-size: 48px; margin-bottom: 12px; }
.audio-name { font-size: 13px; color: var(--text-2, #6b7280); margin-bottom: 16px; }
.preview-audio { width: 100%; min-width: 300px; }

.preview-pdf { width: 100%; height: 65vh; border: none; border-radius: 6px; }

.preview-text-wrap { width: 100%; max-height: 65vh; overflow: auto; }
.text-loading { text-align: center; color: var(--text-3, #9ca3af); padding: 40px; font-size: 13px; }
.preview-text {
  font-family: 'Fira Code', 'Consolas', monospace; font-size: 13px; line-height: 1.6;
  color: var(--text-1, #111827); background: var(--bg-page, #f9fafb);
  padding: 16px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; word-break: break-all;
  border: 1px solid var(--border, #e5e7eb);
}

.preview-unsupported { text-align: center; color: var(--text-3, #9ca3af); font-size: 13px; }
.unsup-icon { font-size: 40px; margin-bottom: 12px; }
.unsup-download {
  display: inline-block; margin-top: 16px; padding: 0 14px; height: 34px; line-height: 34px;
  background: var(--accent, #6366f1); color: #fff; border-radius: 8px;
  text-decoration: none; font-size: 13px; font-weight: 500; transition: opacity 0.15s;
}
.unsup-download:hover { opacity: 0.88; }
</style>
