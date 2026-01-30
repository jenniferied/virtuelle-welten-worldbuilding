<script setup lang="ts">
</script>

<template>
  <div class="soviet-default">
    <div class="default-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.soviet-default {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0D0D0D;
  color: white;
  padding: 3rem;
  display: flex;
  align-items: center;
}

.default-content {
  width: 100%;
  max-width: 80%;
  margin: 0 auto;
}

.default-content :deep(h1) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0 0 1.5rem 0;
}

.default-content :deep(h2) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1.75rem;
  margin: 0 0 1rem 0;
}

.default-content :deep(p) {
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.default-content :deep(ul),
.default-content :deep(ol) {
  margin: 0 0 1rem 1.5rem;
}

.default-content :deep(li) {
  font-size: 1.1rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.default-content :deep(img) {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
}
</style>
