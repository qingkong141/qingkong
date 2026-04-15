<script setup lang="ts">
import { useThemeStore } from './stores/theme'
// 在根组件里初始化主题 store，让 watch 立即生效
useThemeStore()
</script>

<template>
  <router-view />
</template>

<style>
/* ── 全局重置 ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif; }

/* ══════════════════════════════════════
   深色主题变量（默认）
══════════════════════════════════════ */
:root[data-theme="dark"] {
  --bg-page:      #0f0f0f;
  --bg-surface:   #141414;
  --bg-hover:     #1f1f1f;
  --bg-active:    rgba(99, 102, 241, 0.12);
  --bg-input:     #111111;

  --border:       #222222;
  --border-sub:   #2a2a2a;

  --text-1:       #f0f0f0;
  --text-2:       #aaaaaa;
  --text-3:       #555555;
  --text-nav:     #666666;
  --text-nav-act: #818cf8;

  --accent:       #6366f1;
  --accent-end:   #8b5cf6;
  --accent-muted: rgba(99, 102, 241, 0.15);

  --shadow:       0 24px 64px rgba(0, 0, 0, 0.45);
  --shadow-card:  0 2px 12px rgba(0, 0, 0, 0.3);

  --login-glow-1: rgba(99, 102, 241, 0.15);
  --login-glow-2: rgba(139, 92, 246, 0.08);
}

/* ══════════════════════════════════════
   浅色主题变量
══════════════════════════════════════ */
:root[data-theme="light"] {
  --bg-page:      #f5f5f7;
  --bg-surface:   #ffffff;
  --bg-hover:     #f4f4f5;
  --bg-active:    rgba(99, 102, 241, 0.08);
  --bg-input:     #ffffff;

  --border:       #e8e8e8;
  --border-sub:   #ebebeb;

  --text-1:       #111111;
  --text-2:       #555555;
  --text-3:       #aaaaaa;
  --text-nav:     #888888;
  --text-nav-act: #6366f1;

  --accent:       #6366f1;
  --accent-end:   #8b5cf6;
  --accent-muted: rgba(99, 102, 241, 0.08);

  --shadow:       0 24px 64px rgba(0, 0, 0, 0.1);
  --shadow-card:  0 2px 12px rgba(0, 0, 0, 0.06);

  --login-glow-1: rgba(99, 102, 241, 0.08);
  --login-glow-2: rgba(139, 92, 246, 0.04);
}
</style>
