<script setup lang="ts">
defineProps<{
  background: string
  position?: 'bottom' | 'center' | 'top'
  overlay?: 'gradient' | 'dark' | 'none'
}>()
</script>

<template>
  <div class="soviet-hero">
    <!-- Full-bleed background -->
    <div class="hero-bg">
      <img :src="background" alt="" />
      <div
        class="hero-overlay"
        :class="[
          overlay === 'dark' ? 'overlay-dark' : '',
          overlay === 'none' ? 'overlay-none' : '',
          overlay === 'gradient' || !overlay ? 'overlay-gradient' : ''
        ]"
      ></div>
    </div>

    <!-- Content -->
    <div
      class="hero-content"
      :class="[
        position === 'center' ? 'pos-center' : '',
        position === 'top' ? 'pos-top' : '',
        !position || position === 'bottom' ? 'pos-bottom' : ''
      ]"
    >
      <slot />
    </div>
  </div>
</template>

<style scoped>
.soviet-hero {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0D0D0D;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
}

.hero-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
}

.overlay-gradient {
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.85) 0%,
    rgba(0, 0, 0, 0.5) 30%,
    rgba(0, 0, 0, 0.2) 50%,
    transparent 70%
  );
}

.overlay-dark {
  background: rgba(0, 0, 0, 0.6);
}

.overlay-none {
  background: transparent;
}

.hero-content {
  position: absolute;
  left: 0;
  right: 0;
  padding: 3rem;
  color: white;
  z-index: 1;
}

.pos-bottom {
  bottom: 0;
}

.pos-center {
  top: 50%;
  transform: translateY(-50%);
  text-align: center;
}

.pos-top {
  top: 0;
}

.hero-content :deep(h1) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 3rem;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);
}

.hero-content :deep(h2) {
  font-family: 'PT Sans', sans-serif;
  font-weight: 700;
  font-size: 1.75rem;
  margin: 0 0 0.5rem 0;
  opacity: 0.9;
}

.hero-content :deep(p) {
  font-size: 1.1rem;
  line-height: 1.5;
  max-width: 60ch;
  opacity: 0.85;
}
</style>
