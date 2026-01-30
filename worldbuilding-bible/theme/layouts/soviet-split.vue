<script setup lang="ts">
defineProps<{
  image?: string
  imagePosition?: 'left' | 'right'
  imageSize?: '40' | '50' | '60'
}>()
</script>

<template>
  <div
    class="soviet-split"
    :class="[
      imagePosition === 'left' ? 'image-left' : 'image-right',
      `image-size-${imageSize || '50'}`
    ]"
  >
    <!-- Text side -->
    <div class="split-text">
      <div class="text-content">
        <slot />
      </div>
    </div>

    <!-- Image side -->
    <div class="split-image">
      <img v-if="image" :src="image" alt="" />
      <slot name="image" />
    </div>
  </div>
</template>

<style scoped>
.soviet-split {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  background: #0D0D0D;
}

/* Default: image on right */
.image-right {
  flex-direction: row;
}

.image-left {
  flex-direction: row-reverse;
}

/* Size variants */
.image-size-40 .split-text { flex: 0 0 60%; }
.image-size-40 .split-image { flex: 0 0 40%; }

.image-size-50 .split-text { flex: 0 0 50%; }
.image-size-50 .split-image { flex: 0 0 50%; }

.image-size-60 .split-text { flex: 0 0 40%; }
.image-size-60 .split-image { flex: 0 0 60%; }

.split-text {
  display: flex;
  align-items: center;
  padding: 3rem;
  color: white;
}

.text-content {
  max-width: 100%;
}

.text-content :deep(h1) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0 0 1.5rem 0;
  line-height: 1.1;
}

.text-content :deep(h2) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  margin: 0 0 1rem 0;
}

.text-content :deep(p) {
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 1rem 0;
  opacity: 0.9;
}

.text-content :deep(ul),
.text-content :deep(ol) {
  margin: 0 0 1rem 1.5rem;
  padding: 0;
}

.text-content :deep(li) {
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.split-image {
  position: relative;
  overflow: hidden;
}

.split-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.split-image :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
