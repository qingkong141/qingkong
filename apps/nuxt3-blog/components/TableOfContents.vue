<script setup lang="ts">
import type { TocItem } from '~/composables/useMarkdown'

const props = defineProps<{ items: TocItem[] }>()

const activeId = ref('')

onMounted(() => {
  const headings = props.items.map(i => document.getElementById(i.id)).filter(Boolean) as HTMLElement[]
  if (!headings.length) return

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          activeId.value = entry.target.id
          break
        }
      }
    },
    { rootMargin: '-64px 0px -70% 0px', threshold: 0 },
  )

  headings.forEach(el => observer.observe(el))

  onUnmounted(() => observer.disconnect())
})

function scrollTo(id: string) {
  const el = document.getElementById(id)
  if (el) {
    window.scrollTo({ top: el.offsetTop - 80, behavior: 'smooth' })
  }
}
</script>

<template>
  <nav v-if="items.length" class="toc">
    <p class="toc-title">目录</p>
    <ul class="toc-list">
      <li
        v-for="item in items"
        :key="item.id"
        class="toc-item"
        :class="{ active: activeId === item.id }"
        :style="{ paddingLeft: (item.level - 2) * 14 + 'px' }"
      >
        <button @click="scrollTo(item.id)">{{ item.text }}</button>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.toc {
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.toc-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.toc-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-left: 1px solid var(--color-border, #e5e7eb);
}

.toc-item {
  position: relative;
}

.toc-item button {
  display: block;
  width: 100%;
  text-align: left;
  padding: 4px 0 4px 12px;
  font-size: 13px;
  color: var(--color-text-3);
  line-height: 1.5;
  transition: color 0.15s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toc-item button:hover {
  color: var(--color-text-1);
}

.toc-item.active button {
  color: var(--color-accent);
}

.toc-item.active::before {
  content: '';
  position: absolute;
  left: -1px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--color-accent);
}
</style>
