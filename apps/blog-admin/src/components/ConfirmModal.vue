<script setup lang="ts">
defineProps<{
  title?: string
  message: string
  confirmText?: string
  loading?: boolean
  danger?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <div class="modal-mask" @click.self="emit('cancel')">
      <div class="modal">
        <div v-if="danger" class="modal-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <p class="modal-title">{{ title ?? '确认操作' }}</p>
        <p class="modal-msg">{{ message }}</p>
        <div class="modal-actions">
          <button class="m-btn" @click="emit('cancel')">取消</button>
          <button
            class="m-btn"
            :class="danger ? 'm-btn-danger' : 'm-btn-primary'"
            :disabled="loading"
            @click="emit('confirm')"
          >
            {{ loading ? '处理中…' : (confirmText ?? '确认') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
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
  padding: 28px 24px 22px;
  width: 340px;
  box-shadow: 0 20px 60px rgba(0,0,0,.18);
  text-align: center;
}

.modal-icon { margin-bottom: 10px; }

.modal-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-1, #111);
  margin: 0 0 6px;
}

.modal-msg {
  font-size: 13px;
  color: var(--text-2, #6b7280);
  margin: 0 0 20px;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.m-btn {
  flex: 1;
  height: 34px;
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
