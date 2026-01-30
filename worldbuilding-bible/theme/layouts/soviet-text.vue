<script setup lang="ts">
defineProps<{
  columns?: '1' | '2' | '3'
  background?: 'dark' | 'light'
}>()
</script>

<template>
  <div
    class="soviet-text"
    :class="[
      `cols-${columns || '1'}`,
      background === 'light' ? 'bg-light' : 'bg-dark'
    ]"
  >
    <div class="text-container">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.soviet-text {
  position: relative;
  width: 100%;
  height: 100%;
  padding: 3rem;
  overflow: hidden;
}

.bg-dark {
  background: #0D0D0D;
  color: white;
}

.bg-light {
  background: #F8F8F8;
  color: #1A1A1A;
}

.text-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* Single column - centered, max width */
.cols-1 .text-container {
  max-width: 70ch;
  margin: 0 auto;
}

/* Multi-column layouts */
.cols-2 .text-container {
  column-count: 2;
  column-gap: 2rem;
}

.cols-3 .text-container {
  column-count: 3;
  column-gap: 1.5rem;
}

/* Typography */
.soviet-text :deep(h1) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0 0 1.5rem 0;
  column-span: all;
}

.soviet-text :deep(h2) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  margin: 1.5rem 0 1rem 0;
}

.soviet-text :deep(h3) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1.2rem;
  margin: 1rem 0 0.75rem 0;
}

.soviet-text :deep(p) {
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 1rem 0;
  text-align: justify;
  hyphens: auto;
}

.soviet-text :deep(ul),
.soviet-text :deep(ol) {
  margin: 0 0 1rem 1.5rem;
  padding: 0;
}

.soviet-text :deep(li) {
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.soviet-text :deep(blockquote) {
  margin: 1.5rem 0;
  padding: 1rem 1.5rem;
  border-left: 3px solid #888;
  font-style: italic;
  opacity: 0.9;
}

/* Images in text */
.soviet-text :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
}

/* Light theme adjustments */
.bg-light :deep(h1),
.bg-light :deep(h2),
.bg-light :deep(h3) {
  color: #1A1A1A;
}

.bg-light :deep(blockquote) {
  border-left-color: #CCCCCC;
}
</style>
