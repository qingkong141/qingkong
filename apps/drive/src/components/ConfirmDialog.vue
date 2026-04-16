<script setup lang="ts">
import { useConfirm } from '../composables/useConfirm'
const { visible, title, message, confirmText, cancelText, isDanger, confirm, cancel } = useConfirm()
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="modal-mask" @click.self="cancel">
        <div class="modal">
          <h3 class="modal-title">{{ title }}</h3>
          <p class="modal-body">{{ message }}</p>
          <div class="modal-actions">
            <button class="m-btn" @click="cancel">{{ cancelText }}</button>
            <button class="m-btn" :class="isDanger ? 'm-btn-danger' : 'm-btn-primary'" @click="confirm">{{ confirmText }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999; backdrop-filter: blur(2px);
}

.modal {
  background: var(--bg-surface, #fff); border-radius: 14px; padding: 24px;
  width: 360px; max-width: 90vw; box-shadow: 0 20px 60px rgba(0,0,0,.18);
}

.modal-title { font-size: 15px; font-weight: 700; color: var(--text-1, #111); margin: 0 0 8px; }
.modal-body { font-size: 13px; color: var(--text-2, #6b7280); line-height: 1.5; margin: 0 0 18px; }

.modal-actions { display: flex; gap: 8px; justify-content: flex-end; }

.m-btn {
  height: 34px; padding: 0 16px; border-radius: 8px; font-size: 13px; font-weight: 500;
  cursor: pointer; border: 1px solid var(--border, #e5e7eb);
  background: var(--bg-surface, #fff); color: var(--text-1, #111); transition: background 0.12s;
}
.m-btn:hover { background: var(--bg-hover, #f3f4f6); }

.m-btn.m-btn-primary { background: var(--accent, #6366f1); color: #fff; border-color: var(--accent, #6366f1); }
.m-btn.m-btn-primary:hover { background: var(--accent, #6366f1); opacity: .9; }

.m-btn.m-btn-danger { background: #ef4444; color: #fff; border-color: #ef4444; }
.m-btn.m-btn-danger:hover { background: #ef4444; opacity: .9; }

.fade-enter-active { transition: opacity 0.15s; }
.fade-leave-active { transition: opacity 0.1s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
