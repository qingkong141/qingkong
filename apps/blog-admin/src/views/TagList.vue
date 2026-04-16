<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tagApi } from '@qingkong/shared-api'
import type { Tag } from '@qingkong/shared-types'
import { showToast } from '../composables/toast'

const tags = ref<Tag[]>([])
const loading = ref(false)

const showModal = ref(false)
const editing = ref<Tag | null>(null)
const form = ref({ name: '', slug: '', color: '#6366f1' })
const saving = ref(false)

const deleteTarget = ref<Tag | null>(null)
const deleting = ref(false)

const PRESET_COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#ef4444',
  '#f97316', '#eab308', '#22c55e', '#14b8a6',
  '#06b6d4', '#3b82f6', '#6b7280', '#111827',
]

async function fetchTags() {
  loading.value = true
  try {
    tags.value = await tagApi.list()
  } finally {
    loading.value = false
  }
}

onMounted(fetchTags)

function openCreate() {
  editing.value = null
  form.value = { name: '', slug: '', color: '#6366f1' }
  showModal.value = true
}

function openEdit(tag: Tag) {
  editing.value = tag
  form.value = {
    name: tag.name,
    slug: tag.slug,
    color: tag.color || '#6366f1',
  }
  showModal.value = true
}

async function saveTag() {
  if (!form.value.name.trim()) { showToast('请输入标签名称', 'error'); return }
  saving.value = true
  try {
    if (editing.value) {
      await tagApi.update(editing.value.id, {
        name: form.value.name,
        slug: form.value.slug || undefined,
        color: form.value.color || undefined,
      })
      showToast('标签已更新', 'success')
    } else {
      await tagApi.create({
        name: form.value.name,
        slug: form.value.slug || undefined,
        color: form.value.color || undefined,
      })
      showToast('标签已创建', 'success')
    }
    showModal.value = false
    fetchTags()
  } catch {
    showToast('保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function doDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await tagApi.delete(deleteTarget.value.id)
    showToast('标签已删除', 'success')
    deleteTarget.value = null
    fetchTags()
  } catch {
    showToast('删除失败', 'error')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2 class="page-title">标签管理</h2>
        <p class="page-sub">共 {{ tags.length }} 个标签</p>
      </div>
      <button class="btn-new" @click="openCreate()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新建标签
      </button>
    </div>

    <div class="card">
      <!-- 加载 -->
      <div v-if="loading" class="center-state">
        <span class="loading-dot"/><span class="loading-dot"/><span class="loading-dot"/>
      </div>

      <!-- 空 -->
      <div v-else-if="tags.length === 0" class="center-state empty">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.3"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
        <span>暂无标签，<button class="link-btn" @click="openCreate()">立即创建</button></span>
      </div>

      <!-- 标签网格 -->
      <div v-else class="tag-grid">
        <div v-for="tag in tags" :key="tag.id" class="tag-card">
          <div class="tag-card-header">
            <span class="tag-dot" :style="{ background: tag.color || '#6366f1' }"/>
            <span class="tag-name">{{ tag.name }}</span>
          </div>
          <div class="tag-slug">{{ tag.slug }}</div>
          <div class="tag-card-actions">
            <button class="act-btn" @click="openEdit(tag)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              编辑
            </button>
            <button class="act-btn danger" @click="deleteTarget = tag">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-mask" @click.self="showModal = false">
        <div class="modal">
          <p class="modal-title">{{ editing ? '编辑标签' : '新建标签' }}</p>

          <div class="form-group">
            <label class="form-label">名称 <span class="required">*</span></label>
            <input v-model="form.name" class="form-input" placeholder="标签名称" />
          </div>

          <div class="form-group">
            <label class="form-label">Slug</label>
            <input v-model="form.slug" class="form-input" placeholder="留空则自动生成" />
          </div>

          <div class="form-group">
            <label class="form-label">颜色</label>
            <div class="color-picker">
              <div class="color-presets">
                <button
                  v-for="c in PRESET_COLORS"
                  :key="c"
                  class="color-swatch"
                  :class="{ active: form.color === c }"
                  :style="{ background: c }"
                  @click="form.color = c"
                />
              </div>
              <div class="color-custom">
                <input type="color" v-model="form.color" class="color-native" />
                <input v-model="form.color" class="form-input color-hex" placeholder="#hex" />
              </div>
            </div>
            <div class="color-preview">
              <span class="preview-chip" :style="{ background: form.color + '18', color: form.color, borderColor: form.color + '40' }">
                <span class="preview-dot" :style="{ background: form.color }"/>
                预览效果
              </span>
            </div>
          </div>

          <div class="modal-actions">
            <button class="m-btn" @click="showModal = false">取消</button>
            <button class="m-btn m-btn-primary" :disabled="saving" @click="saveTag">
              {{ saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-mask" @click.self="deleteTarget = null">
        <div class="modal">
          <div class="modal-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <p class="modal-title" style="text-align:center">确认删除</p>
          <p class="modal-msg">确定删除标签「{{ deleteTarget.name }}」？已关联的文章不会被删除。</p>
          <div class="modal-actions" style="justify-content:center">
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

.btn-new {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 14px;
  background: var(--accent, #6366f1);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.btn-new:hover { opacity: 0.88; }

.card {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px;
  overflow: hidden;
}

.center-state {
  text-align: center;
  padding: 48px 16px;
  color: var(--text-3, #9ca3af);
}
.center-state svg { display: block; margin: 0 auto 10px; }
.center-state span { font-size: 13px; }

.link-btn {
  background: none;
  border: none;
  color: var(--accent, #6366f1);
  cursor: pointer;
  font-size: 13px;
  padding: 0;
  text-decoration: underline;
}

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

/* ── 标签网格 ── */
.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  padding: 16px;
}

.tag-card {
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.tag-card:hover {
  border-color: var(--accent, #6366f1);
  box-shadow: 0 2px 12px rgba(99,102,241,.08);
}

.tag-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-1, #111827);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-slug {
  font-size: 12px;
  color: var(--text-3, #9ca3af);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-card-actions {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

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
.act-btn.danger:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: rgba(239,68,68,.05);
}

/* ── 弹窗 ── */
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
  padding: 24px;
  width: 380px;
  box-shadow: 0 20px 60px rgba(0,0,0,.18);
}

.modal-icon { text-align: center; margin-bottom: 10px; }
.modal-title { font-size: 15px; font-weight: 700; color: var(--text-1, #111); margin: 0 0 16px; }
.modal-msg { font-size: 13px; color: var(--text-2, #6b7280); margin: 0 0 20px; line-height: 1.6; text-align: center; }

.form-group { margin-bottom: 14px; }

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-2, #6b7280);
  margin-bottom: 5px;
}

.required { color: #ef4444; }

.form-input {
  width: 100%;
  height: 34px;
  padding: 0 10px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 7px;
  background: var(--bg-page, #f5f5f7);
  color: var(--text-1, #111);
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s;
}
.form-input:focus { border-color: var(--accent, #6366f1); }

/* 颜色选择器 */
.color-picker {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.color-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.12s, border-color 0.12s;
  padding: 0;
}
.color-swatch:hover { transform: scale(1.15); }
.color-swatch.active {
  border-color: var(--text-1, #111);
  box-shadow: 0 0 0 2px var(--bg-surface, #fff);
}

.color-custom {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-native {
  width: 34px;
  height: 34px;
  padding: 0;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 7px;
  cursor: pointer;
  background: none;
  flex-shrink: 0;
}

.color-hex {
  flex: 1;
  font-family: 'SF Mono', Menlo, monospace;
  font-size: 12px;
}

.color-preview {
  margin-top: 4px;
}

.preview-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
}

.preview-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 18px;
}

.m-btn {
  height: 34px;
  padding: 0 16px;
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

.m-btn-primary {
  background: var(--accent, #6366f1);
  color: #fff;
  border-color: var(--accent, #6366f1);
}
.m-btn-primary:hover { opacity: .9; }
.m-btn-primary:disabled { opacity: .5; cursor: not-allowed; }

.m-btn-danger { background: #ef4444; color: #fff; border-color: #ef4444; }
.m-btn-danger:hover { opacity: .9; }
.m-btn-danger:disabled { opacity: .5; cursor: not-allowed; }
</style>
