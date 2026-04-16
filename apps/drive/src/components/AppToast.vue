<script setup lang="ts">
import { useToast } from '../composables/useToast'
const { toasts } = useToast()
</script>

<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-stack">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type">
        {{ t.message }}
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<style scoped>
.toast-stack {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  z-index: 9999;
  pointer-events: none;
}

.toast {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.14);
  white-space: nowrap;
  pointer-events: auto;
}

.toast.info    { background: #1e1e2e; color: #fff; }
.toast.success { background: #16a34a; color: #fff; }
.toast.error   { background: #dc2626; color: #fff; }
.toast.warning { background: #d97706; color: #fff; }

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-enter-from { opacity: 0; transform: translateY(-8px); }
.toast-leave-to   { opacity: 0; transform: translateY(-8px); }
</style>
