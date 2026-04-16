<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { categoryApi } from '@qingkong/shared-api'
import type { Category } from '@qingkong/shared-types'
import { showToast } from '../composables/toast'
import ConfirmModal from '../components/ConfirmModal.vue'
import LoadingDots from '../components/LoadingDots.vue'
import EmptyState from '../components/EmptyState.vue'

const tree = ref<Category[]>([])
const loading = ref(false)

const expanded = ref<Set<number>>(new Set())

const showModal = ref(false)
const editing = ref<Category | null>(null)
const form = ref({ name: '', slug: '', description: '', parentId: undefined as number | undefined })
const saving = ref(false)

const deleteTarget = ref<Category | null>(null)
const deleting = ref(false)

interface FlatRow {
  cat: Category
  depth: number
  hasChildren: boolean
}

const flatRows = computed<FlatRow[]>(() => {
  const rows: FlatRow[] = []
  function walk(cats: Category[], depth: number) {
    for (const cat of cats) {
      const hasChildren = !!(cat.children?.length)
      rows.push({ cat, depth, hasChildren })
      if (hasChildren && expanded.value.has(cat.id)) {
        walk(cat.children!, depth + 1)
      }
    }
  }
  walk(tree.value, 0)
  return rows
})

async function fetchCategories() {
  loading.value = true
  try {
    tree.value = await categoryApi.list()
    tree.value.forEach(function expandAll(c: Category) {
      expanded.value.add(c.id)
      c.children?.forEach(expandAll)
    })
  } finally {
    loading.value = false
  }
}

onMounted(fetchCategories)

function flattenForSelect(cats: Category[], depth = 0, excludeId?: number): { id: number; label: string }[] {
  const result: { id: number; label: string }[] = []
  for (const c of cats) {
    if (c.id === excludeId) continue
    result.push({ id: c.id, label: '\u00a0'.repeat(depth * 4) + c.name })
    if (c.children?.length) {
      result.push(...flattenForSelect(c.children, depth + 1, excludeId))
    }
  }
  return result
}

function openCreate(parentId?: number) {
  editing.value = null
  form.value = { name: '', slug: '', description: '', parentId }
  showModal.value = true
}

function openEdit(cat: Category) {
  editing.value = cat
  form.value = {
    name: cat.name,
    slug: cat.slug,
    description: cat.description ?? '',
    parentId: cat.parentId ?? undefined,
  }
  showModal.value = true
}

async function saveCategory() {
  if (!form.value.name.trim()) { showToast('请输入分类名称', 'error'); return }
  saving.value = true
  try {
    if (editing.value) {
      await categoryApi.update(editing.value.id, {
        name: form.value.name,
        slug: form.value.slug || undefined,
        description: form.value.description || undefined,
      })
      showToast('分类已更新', 'success')
    } else {
      await categoryApi.create({
        name: form.value.name,
        slug: form.value.slug || undefined,
        description: form.value.description || undefined,
        parentId: form.value.parentId,
      })
      showToast('分类已创建', 'success')
    }
    showModal.value = false
    fetchCategories()
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
    await categoryApi.delete(deleteTarget.value.id)
    showToast('分类已删除', 'success')
    deleteTarget.value = null
    fetchCategories()
  } catch {
    showToast('删除失败', 'error')
  } finally {
    deleting.value = false
  }
}

function toggleExpand(id: number) {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
}

function countChildren(cat: Category): number {
  return (cat.children?.length ?? 0) + (cat.children?.reduce((s, c) => s + countChildren(c), 0) ?? 0)
}

const parentOptions = computed(() => flattenForSelect(tree.value, 0, editing.value?.id))
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2 class="page-title">分类管理</h2>
        <p class="page-sub">管理文章分类，支持多级结构</p>
      </div>
      <button class="btn-new" @click="openCreate()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新建分类
      </button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th style="width:40%">名称</th>
            <th>Slug</th>
            <th>描述</th>
            <th>子分类数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5"><LoadingDots /></td>
          </tr>
          <tr v-else-if="tree.length === 0">
            <td colspan="5">
              <EmptyState>
                <template #icon>
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.3"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                </template>
                暂无分类，<button class="link-btn" @click="openCreate()">立即创建</button>
              </EmptyState>
            </td>
          </tr>
          <tr
            v-else
            v-for="row in flatRows"
            :key="row.cat.id"
            class="data-row"
          >
            <td :style="{ paddingLeft: (16 + row.depth * 28) + 'px' }">
              <div class="td-name">
                <button
                  v-if="row.hasChildren"
                  class="expand-btn"
                  @click="toggleExpand(row.cat.id)"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" :style="{ transform: expanded.has(row.cat.id) ? 'rotate(90deg)' : '' }">
                    <polyline points="9 18 15 12 9 6"/>
                  </svg>
                </button>
                <span v-else class="expand-placeholder"/>
                <span class="cat-icon" :class="{ sub: row.depth > 0 }">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                </span>
                <span class="cat-name">{{ row.cat.name }}</span>
              </div>
            </td>
            <td class="td-meta">{{ row.cat.slug }}</td>
            <td class="td-meta td-desc" :title="row.cat.description ?? ''">{{ row.cat.description || '—' }}</td>
            <td class="td-meta">{{ countChildren(row.cat) }}</td>
            <td>
              <div class="td-actions">
                <button class="act-btn" @click="openCreate(row.cat.id)" title="添加子分类">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                </button>
                <button class="act-btn" @click="openEdit(row.cat)">编辑</button>
                <button class="act-btn danger" @click="deleteTarget = row.cat">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新建/编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-mask" @click.self="showModal = false">
        <div class="modal">
          <p class="modal-title">{{ editing ? '编辑分类' : '新建分类' }}</p>

          <div class="form-group">
            <label class="form-label">名称 <span class="required">*</span></label>
            <input v-model="form.name" class="form-input" placeholder="分类名称" />
          </div>

          <div class="form-group">
            <label class="form-label">Slug</label>
            <input v-model="form.slug" class="form-input" placeholder="留空则自动生成" />
          </div>

          <div class="form-group" v-if="!editing">
            <label class="form-label">上级分类</label>
            <select v-model="form.parentId" class="form-input">
              <option :value="undefined">— 顶级分类 —</option>
              <option
                v-for="opt in parentOptions"
                :key="opt.id"
                :value="opt.id"
              >{{ opt.label }}</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea v-model="form.description" class="form-textarea" rows="2" placeholder="可选描述…"/>
          </div>

          <div class="modal-actions">
            <button class="m-btn" @click="showModal = false">取消</button>
            <button class="m-btn m-btn-primary" :disabled="saving" @click="saveCategory">
              {{ saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <ConfirmModal
      v-if="deleteTarget"
      danger
      title="确认删除"
      :message="`确定删除分类「${deleteTarget.name}」？其下的子分类也将被删除。`"
      confirm-text="确认删除"
      :loading="deleting"
      @confirm="doDelete"
      @cancel="deleteTarget = null"
    />
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

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th {
  padding: 10px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-3, #9ca3af);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: var(--bg-page, #f9fafb);
  border-bottom: 1px solid var(--border, #e5e7eb);
  white-space: nowrap;
}

.table td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border, #e5e7eb);
  color: var(--text-1, #111827);
  vertical-align: middle;
}

.table tbody tr:last-child td { border-bottom: none; }

.data-row { transition: background 0.12s; }
.data-row:hover td { background: var(--bg-hover, #f5f5ff); }

.td-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-3, #9ca3af);
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
  flex-shrink: 0;
}
.expand-btn:hover { color: var(--accent, #6366f1); background: var(--bg-hover, #f3f4f6); }
.expand-btn svg { transition: transform 0.2s; }

.expand-placeholder { width: 16px; flex-shrink: 0; }

.cat-icon { color: var(--accent, #6366f1); display: flex; flex-shrink: 0; }
.cat-icon.sub { color: var(--text-3, #9ca3af); }

.cat-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-meta { color: var(--text-2, #6b7280); }

.td-desc {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-btn {
  background: none;
  border: none;
  color: var(--accent, #6366f1);
  cursor: pointer;
  font-size: 13px;
  padding: 0;
  text-decoration: underline;
}

.td-actions { display: flex; gap: 4px; }

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

/* ── 编辑弹窗 ── */
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

.modal-title { font-size: 15px; font-weight: 700; color: var(--text-1, #111); margin: 0 0 16px; }

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
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.form-input:focus {
  border-color: var(--accent, #6366f1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 7px;
  background: var(--bg-surface, #fff);
  color: var(--text-1, #111);
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.form-textarea:focus {
  border-color: var(--accent, #6366f1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
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
</style>
