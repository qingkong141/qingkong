<script setup lang="ts">
const route = useRoute()

const navLinks = [
  { label: '首页', path: '/' },
  { label: '归档', path: '/archives' },
  { label: '分类', path: '/categories' },
  { label: '标签', path: '/tags' },
  { label: '关于', path: '/about' },
]

const mobileMenuOpen = ref(false)

watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <div class="site">
    <!-- Header -->
    <header class="site-header">
      <div class="container header-inner">
        <NuxtLink to="/" class="logo">
          <span class="logo-icon">◈</span>
          <span class="logo-text">青空</span>
        </NuxtLink>

        <nav class="desktop-nav">
          <NuxtLink
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="nav-link"
            :class="{ active: isActive(link.path) }"
          >
            {{ link.label }}
          </NuxtLink>
        </nav>

        <button class="mobile-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
          <span :class="['hamburger', { open: mobileMenuOpen }]">
            <span /><span /><span />
          </span>
        </button>
      </div>

      <!-- Mobile menu -->
      <Transition name="slide">
        <div v-if="mobileMenuOpen" class="mobile-nav">
          <NuxtLink
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="mobile-link"
            :class="{ active: isActive(link.path) }"
          >
            {{ link.label }}
          </NuxtLink>
        </div>
      </Transition>
    </header>

    <!-- Main content -->
    <main class="site-main">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="site-footer">
      <div class="container footer-inner">
        <p class="footer-copy">© {{ new Date().getFullYear() }} 青空 QingKong</p>
        <p class="footer-powered">Powered by Nuxt 3 & FastAPI</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.site {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ── Header ─────────────────── */
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-light);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-height);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-1);
  transition: opacity 0.2s;
}

.logo:hover { opacity: 0.8; }

.logo-icon {
  color: var(--color-accent);
  font-size: 22px;
}

.desktop-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-2);
  transition: color 0.15s, background 0.15s;
}

.nav-link:hover {
  color: var(--color-text-1);
  background: var(--color-accent-light);
}

.nav-link.active {
  color: var(--color-accent);
  background: var(--color-accent-light);
}

/* ── Mobile toggle ─────────── */
.mobile-toggle {
  display: none;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
}

.hamburger {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 20px;
}

.hamburger span {
  display: block;
  height: 2px;
  background: var(--color-text-1);
  border-radius: 2px;
  transition: transform 0.25s, opacity 0.25s;
}

.hamburger.open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.hamburger.open span:nth-child(2) {
  opacity: 0;
}
.hamburger.open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

.mobile-nav {
  display: none;
  flex-direction: column;
  padding: 8px 24px 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.mobile-link {
  padding: 10px 0;
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-2);
  border-bottom: 1px solid var(--color-border-light);
  transition: color 0.15s;
}

.mobile-link:last-child {
  border-bottom: none;
}

.mobile-link.active {
  color: var(--color-accent);
}

.slide-enter-active, .slide-leave-active {
  transition: max-height 0.3s ease, opacity 0.2s ease;
  overflow: hidden;
}
.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
}
.slide-enter-to, .slide-leave-from {
  max-height: 300px;
  opacity: 1;
}

@media (max-width: 768px) {
  .desktop-nav { display: none; }
  .mobile-toggle { display: flex; }
  .mobile-nav { display: flex; }
}

/* ── Main ──────────────────── */
.site-main {
  flex: 1;
  padding: 40px 0;
}

@media (max-width: 768px) {
  .site-main { padding: 24px 0; }
}

/* ── Footer ────────────────── */
.site-footer {
  border-top: 1px solid var(--color-border-light);
  padding: 32px 0;
  margin-top: auto;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-copy {
  font-size: 13px;
  color: var(--color-text-3);
}

.footer-powered {
  font-size: 12px;
  color: var(--color-text-3);
}

@media (max-width: 768px) {
  .footer-inner {
    flex-direction: column;
    gap: 4px;
    text-align: center;
  }
}
</style>
