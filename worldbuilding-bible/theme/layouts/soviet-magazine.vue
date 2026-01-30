<script setup lang="ts">
defineProps<{
  columns?: '1' | '2' | '3'
  title?: string
  subtitle?: string
  dense?: boolean
}>()
</script>

<template>
  <div class="soviet-magazine" :class="{ dense }">
    <!-- Header -->
    <div v-if="title" class="magazine-header">
      <h1>{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>

    <!-- Content columns -->
    <div
      class="magazine-content"
      :class="[`cols-${columns || '2'}`]"
    >
      <slot />
    </div>
  </div>
</template>

<style scoped>
.soviet-magazine {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0D0D0D;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 1.25rem 2rem;
  overflow: hidden;
}

.soviet-magazine.dense {
  padding: 1rem 1.75rem;
}

.magazine-header {
  flex: 0 0 auto;
  margin-bottom: 0.75rem;
  border-bottom: 2px solid #E85A6B;
  padding-bottom: 0.5rem;
}

.magazine-header h1 {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin: 0;
  color: white;
}

.magazine-header .subtitle {
  font-size: 0.8rem;
  color: #888888;
  margin: 0.25rem 0 0 0;
}

.magazine-content {
  flex: 1;
  display: grid;
  gap: 1.5rem;
  overflow: hidden;
}

.cols-1 {
  grid-template-columns: 1fr;
}

.cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

/* Dense text styling */
.soviet-magazine :deep(p) {
  font-size: 0.75rem;
  line-height: 1.4;
  margin: 0 0 0.5rem 0;
  text-align: justify;
  hyphens: auto;
}

.soviet-magazine.dense :deep(p) {
  font-size: 0.7rem;
  line-height: 1.35;
  margin: 0 0 0.35rem 0;
}

.soviet-magazine :deep(h2) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1rem;
  margin: 0 0 0.5rem 0;
  color: #E85A6B;
}

.soviet-magazine :deep(h3) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 0.85rem;
  margin: 0 0 0.35rem 0;
  color: white;
}

.soviet-magazine :deep(strong) {
  color: #E85A6B;
}

.soviet-magazine :deep(em) {
  font-style: italic;
  color: #B4C7D4;
}

.soviet-magazine :deep(ul),
.soviet-magazine :deep(ol) {
  padding-left: 1rem;
  margin: 0 0 0.5rem 0;
}

.soviet-magazine :deep(li) {
  font-size: 0.75rem;
  line-height: 1.35;
  margin-bottom: 0.15rem;
}

.soviet-magazine.dense :deep(li) {
  font-size: 0.7rem;
}

/* Drop cap effect for first paragraph */
.soviet-magazine :deep(.drop-cap::first-letter) {
  float: left;
  font-size: 2.5rem;
  line-height: 1;
  padding-right: 0.35rem;
  color: #E85A6B;
  font-weight: 700;
}

/* Image in column */
.soviet-magazine :deep(img) {
  width: 100%;
  height: auto;
  object-fit: cover;
  margin-bottom: 0.5rem;
}

.soviet-magazine :deep(figure) {
  margin: 0 0 1rem 0;
}

.soviet-magazine :deep(figcaption) {
  font-size: 0.65rem;
  color: #E85A6B;
  text-align: right;
}
</style>
