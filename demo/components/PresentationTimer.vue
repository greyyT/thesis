<template>
  <div v-if="showTimer" class="fixed top-4 right-4 bg-gray-800 bg-opacity-80 text-white p-3 rounded-lg shadow-lg">
    <div class="text-sm font-mono">
      <div class="text-xs opacity-70 mb-1">Time Remaining</div>
      <div class="text-2xl font-bold" :class="timeClass">
        {{ formatTime }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  minutes?: number
  showTimer?: boolean
}>()

const totalSeconds = ref((props.minutes || 10) * 60)
const interval = ref<number>()

const formatTime = computed(() => {
  const mins = Math.floor(totalSeconds.value / 60)
  const secs = totalSeconds.value % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
})

const timeClass = computed(() => {
  if (totalSeconds.value <= 60) return 'text-red-500'
  if (totalSeconds.value <= 180) return 'text-yellow-500'
  return 'text-green-500'
})

onMounted(() => {
  interval.value = setInterval(() => {
    if (totalSeconds.value > 0) {
      totalSeconds.value--
    }
  }, 1000)
})

onUnmounted(() => {
  if (interval.value) {
    clearInterval(interval.value)
  }
})
</script>