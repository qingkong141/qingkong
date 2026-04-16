<script setup lang="ts">
const progress = ref(0)

function update() {
  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  progress.value = docHeight > 0 ? Math.min((scrollTop / docHeight) * 100, 100) : 0
}

onMounted(() => {
  window.addEventListener('scroll', update, { passive: true })
  update()
})

onUnmounted(() => {
  window.removeEventListener('scroll', update)
})
</script>

<template>
  <div class="reading-progress" :style="{ width: progress + '%' }" />
</template>

<style scoped>
.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 2px;
  background: var(--color-accent, #6366f1);
  z-index: 200;
  transition: width 0.1s linear;
}
</style>
