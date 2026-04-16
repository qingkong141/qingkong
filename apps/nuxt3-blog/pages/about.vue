<script setup lang="ts">
useHead({ title: '关于 - 青空' })
</script>

<template>
  <div class="container">
    <article class="about">
      <h1 class="about-title">关于</h1>
      <div class="about-content">
        <p>青空 QingKong — 一个记录技术与生活的个人博客。</p>
        <p>这里会分享编程笔记、技术探索和日常思考。</p>
      </div>
    </article>
  </div>
</template>

<style scoped>
.about {
  max-width: 600px;
  margin: 0 auto;
}

.about-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
}

.about-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--color-text-2);
}

.about-content p {
  margin-bottom: 1em;
}
</style>
