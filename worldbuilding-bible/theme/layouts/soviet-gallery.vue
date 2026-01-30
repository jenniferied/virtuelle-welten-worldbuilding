<script setup lang="ts">
defineProps<{
  columns?: '2' | '3' | '4'
  rows?: '1' | '2' | '3'
  gap?: 'none' | 'small' | 'medium'
  title?: string
}>()
</script>

<template>
  <div class="soviet-gallery">
    <!-- Optional title bar -->
    <div v-if="title" class="gallery-header">
      <h2>{{ title }}</h2>
    </div>

    <!-- Image grid -->
    <div
      class="gallery-grid"
      :class="[
        `cols-${columns || '2'}`,
        `rows-${rows || '2'}`,
        `gap-${gap || 'small'}`
      ]"
      :style="{
        '--gallery-cols': columns || '2',
        '--gallery-rows': rows || '2'
      }"
    >
      <slot />
    </div>
  </div>
</template>

<style scoped>
.soviet-gallery {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0D0D0D;
  display: flex;
  flex-direction: column;
}

.gallery-header {
  flex: 0 0 auto;
  padding: 1.5rem 2rem 0.5rem;
  color: white;
}

.gallery-header h2 {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  margin: 0;
}

.gallery-grid {
  flex: 1;
  display: grid;
  padding: 1rem;
  overflow: hidden;
}

/* Column variants */
.cols-2 { grid-template-columns: repeat(2, 1fr); }
.cols-3 { grid-template-columns: repeat(3, 1fr); }
.cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Row variants */
.rows-1 { grid-template-rows: 1fr; }
.rows-2 { grid-template-rows: repeat(2, 1fr); }
.rows-3 { grid-template-rows: repeat(3, 1fr); }

/* Gap variants */
.gap-none { gap: 0; }
.gap-small { gap: 0.5rem; }
.gap-medium { gap: 1rem; }

/* Images auto-fit to grid cells */
.gallery-grid :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.gallery-grid :deep(figure) {
  margin: 0;
  position: relative;
  overflow: hidden;
}

.gallery-grid :deep(figcaption) {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.5rem;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  color: white;
  font-size: 0.7rem;
  font-family: 'PT Sans', sans-serif;
}
</style>
