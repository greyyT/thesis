<script setup lang="ts">
import { computed } from "vue";
import { useNav } from "@slidev/client";

const { currentSlideRoute, total } = useNav();

const formatter = computed(
  () => (currentSlideRoute.value.meta?.slide as any)?.frontmatter || {}
);
const enableGlow = computed(() => formatter.value.glow !== false);
const glowOpacity = computed(() => formatter.value.glowOpacity || 0.3);

// Page numbering
const currentSlideNo = computed(
  () => currentSlideRoute.value.meta?.slide?.no || 1
);
const showPageNumber = computed(() => {
  // Don't show page number on the first slide (title slide)
  return currentSlideNo.value > 1;
});
</script>

<template>
  <div v-if="enableGlow">
    <div
      class="glow-container"
      :style="{ opacity: glowOpacity }"
      aria-hidden="true"
    >
      <div class="glow glow-1" />
      <div class="glow glow-2" />
      <div class="glow glow-3" />
    </div>
  </div>

  <!-- Page number -->
  <div v-if="showPageNumber" class="page-number">
    {{ currentSlideNo }} / {{ total }}
  </div>
</template>

<style scoped>
.glow-container {
  position: absolute;
  inset: 0;
  z-index: -10;
  overflow: hidden;
  pointer-events: none;
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  transition: all 3s ease;
}

.glow-1 {
  top: -20%;
  left: -20%;
  width: 60%;
  height: 60%;
  background: radial-gradient(circle, #3b82f6 0%, transparent 70%);
  animation: float-1 20s ease-in-out infinite;
}

.glow-2 {
  bottom: -30%;
  right: -30%;
  width: 70%;
  height: 70%;
  background: radial-gradient(circle, #8b5cf6 0%, transparent 70%);
  animation: float-2 25s ease-in-out infinite;
}

.glow-3 {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40%;
  height: 40%;
  background: radial-gradient(circle, #10b981 0%, transparent 70%);
  animation: float-3 30s ease-in-out infinite;
}

@keyframes float-1 {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(10%, 10%) scale(1.1);
  }
  66% {
    transform: translate(-10%, 5%) scale(0.9);
  }
}

@keyframes float-2 {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(-10%, -10%) scale(0.9);
  }
  66% {
    transform: translate(5%, -5%) scale(1.1);
  }
}

@keyframes float-3 {
  0%,
  100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
  }
}

/* Page number styling */
.page-number {
  position: fixed;
  bottom: 20px;
  right: 30px;
  font-size: 14px;
  color: #9ca3af;
  font-family: "DM Sans", sans-serif;
  font-weight: 500;
  z-index: 100;
  background: rgba(0, 0, 0, 0.5);
  padding: 4px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
}
</style>
