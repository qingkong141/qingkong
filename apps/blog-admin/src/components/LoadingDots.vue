<template>
  <div class="loading-dots">
    <span class="dot"/><span class="dot"/><span class="dot"/>
  </div>
</template>

<style scoped>
.loading-dots {
  text-align: center;
  padding: 32px 16px;
}

.dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin: 0 3px;
  border-radius: 50%;
  background: var(--accent, #6366f1);
  animation: pulse 1.2s ease-in-out infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse { 0%,80%,100% { opacity: .3; transform: scale(.8); } 40% { opacity: 1; transform: scale(1); } }
</style>
