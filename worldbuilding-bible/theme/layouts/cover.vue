<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  background?: string
  subtitle?: string
  author?: string
  date?: string
}>()
</script>

<template>
  <div class="soviet-cover">
    <!-- Background image if provided -->
    <div v-if="background" class="cover-bg">
      <img :src="background" alt="" />
      <div class="cover-overlay"></div>
    </div>

    <!-- Content -->
    <div class="cover-content">
      <div class="cover-title">
        <slot />
      </div>
      <div v-if="subtitle" class="cover-subtitle">{{ subtitle }}</div>
      <div class="cover-meta">
        <span v-if="author">{{ author }}</span>
        <span v-if="author && date"> · </span>
        <span v-if="date">{{ date }}</span>
      </div>
    </div>

    <!-- Logo area -->
    <div class="cover-footer">
      <div class="cover-institution">
        Technische Hochschule Ostwestfalen-Lippe<br/>
        Master Medienproduktion
      </div>
    </div>
  </div>
</template>

<style scoped>
.soviet-cover {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0D0D0D;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.cover-bg {
  position: absolute;
  inset: 0;
}

.cover-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
}

.cover-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 2rem;
}

.cover-title {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 5rem;
  letter-spacing: 0.05em;
  color: white;
  text-transform: uppercase;
}

.cover-title :deep(h1) {
  font-size: inherit;
  letter-spacing: inherit;
  margin: 0;
}

.cover-subtitle {
  font-family: 'PT Sans', sans-serif;
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 1.5rem;
  font-style: italic;
}

.cover-meta {
  font-family: 'PT Mono', monospace;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 2rem;
}

.cover-footer {
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  text-align: right;
}

.cover-institution {
  font-family: 'PT Sans', sans-serif;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.4;
}
</style>
