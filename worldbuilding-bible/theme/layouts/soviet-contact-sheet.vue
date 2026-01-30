<script setup lang="ts">
defineProps<{
  columns?: '4' | '6' | '8'
  rows?: '2' | '3' | '4' | '6'
  caption?: string
  title?: string
}>()
</script>

<template>
  <div class="soviet-contact-sheet">
    <!-- Optional title -->
    <div v-if="title" class="sheet-header">
      <h2>{{ title }}</h2>
    </div>

    <!-- Image grid -->
    <div
      class="sheet-grid"
      :style="{
        '--grid-cols': columns || '4',
        '--grid-rows': rows || '4'
      }"
    >
      <slot />
    </div>

    <!-- Caption -->
    <div v-if="caption" class="sheet-caption">
      {{ caption }}
    </div>
  </div>
</template>

<style scoped>
.soviet-contact-sheet {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0D0D0D;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.sheet-header {
  flex: 0 0 auto;
  padding: 1rem 1.5rem 0.5rem;
}

.sheet-header h2 {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1.25rem;
  text-transform: uppercase;
  color: white;
  margin: 0;
}

.sheet-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(var(--grid-cols), 1fr);
  grid-template-rows: repeat(var(--grid-rows), 1fr);
  gap: 2px;
  padding: 2px;
  background: #0D0D0D;
  overflow: hidden;
}

/* Images auto-fit to grid cells */
.sheet-grid :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.sheet-grid :deep(figure) {
  margin: 0;
  overflow: hidden;
  background: #1A1A1A;
}

.sheet-grid :deep(div) {
  overflow: hidden;
  background: #1A1A1A;
}

.sheet-caption {
  flex: 0 0 auto;
  padding: 0.75rem 1.5rem;
  font-family: 'PT Sans', sans-serif;
  font-size: 0.85rem;
  color: #E85A6B;
  text-align: left;
}
</style>
