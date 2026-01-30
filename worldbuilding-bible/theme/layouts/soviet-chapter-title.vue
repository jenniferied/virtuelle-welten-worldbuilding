<script setup lang="ts">
defineProps<{
  chapter?: string
  background?: string
  position?: 'center' | 'bottom' | 'top'
}>()
</script>

<template>
  <div class="soviet-chapter-title">
    <!-- Background image -->
    <img v-if="background" :src="background" class="bg-image" alt="" />
    <div class="overlay"></div>

    <!-- Content -->
    <div class="content" :class="position || 'center'">
      <div v-if="chapter" class="chapter-number">{{ chapter }}</div>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.soviet-chapter-title {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0D0D0D;
  overflow: hidden;
}

.bg-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(13, 13, 13, 0.95) 0%,
    rgba(13, 13, 13, 0.6) 40%,
    rgba(13, 13, 13, 0.3) 70%,
    transparent 100%
  );
}

.content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  padding: 3rem 4rem;
  color: white;
}

.content.center {
  justify-content: center;
  align-items: center;
  text-align: center;
}

.content.bottom {
  justify-content: flex-end;
  align-items: flex-start;
  text-align: left;
}

.content.top {
  justify-content: flex-start;
  align-items: flex-start;
  text-align: left;
  padding-top: 4rem;
}

.chapter-number {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 6rem;
  line-height: 1;
  color: #E85A6B;
  opacity: 0.8;
  margin-bottom: 1rem;
}

.content.center .chapter-number {
  font-size: 8rem;
}

.content :deep(h1) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 3rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
  color: white;
}

.content.center :deep(h1) {
  font-size: 3.5rem;
}

.content :deep(p) {
  font-size: 1.25rem;
  color: #888888;
  margin: 1rem 0 0 0;
  max-width: 600px;
}
</style>
