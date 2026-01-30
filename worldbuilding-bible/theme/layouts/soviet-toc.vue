<script setup lang="ts">
defineProps<{
  image?: string
  imagePosition?: 'left' | 'right'
}>()
</script>

<template>
  <div class="soviet-toc">
    <!-- Image side (40%) -->
    <div class="toc-image" :class="imagePosition === 'right' ? 'order-2' : 'order-1'">
      <img v-if="image" :src="image" alt="Table of Contents Illustration" />
    </div>

    <!-- Content side (60%) -->
    <div class="toc-content" :class="imagePosition === 'right' ? 'order-1' : 'order-2'">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.soviet-toc {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0D0D0D;
  display: flex;
  overflow: hidden;
}

.toc-image {
  flex: 0 0 40%;
  position: relative;
  overflow: hidden;
}

.toc-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.toc-content {
  flex: 0 0 60%;
  padding: 3rem 4rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
  overflow: hidden;
}

.toc-content :deep(h1),
.toc-content :deep(h2) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0 0 2rem 0;
  color: white;
}

.toc-content :deep(h1) {
  font-size: 2.5rem;
  letter-spacing: 0.05em;
}

.toc-content :deep(ul),
.toc-content :deep(ol) {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-content :deep(li) {
  font-family: 'PT Sans', sans-serif;
  font-size: 1.1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.toc-content :deep(li:last-child) {
  border-bottom: none;
}

.toc-content :deep(li strong) {
  color: #E85A6B;
  font-weight: 700;
}

.toc-content :deep(a) {
  color: white;
  text-decoration: none;
}

.toc-content :deep(a:hover) {
  color: #E85A6B;
}

.order-1 { order: 1; }
.order-2 { order: 2; }
</style>
