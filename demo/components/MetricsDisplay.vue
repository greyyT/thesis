<template>
  <div class="metrics-container">
    <div
      v-for="(metric, index) in metrics"
      :key="index"
      class="metric-card"
      :class="metric.class"
      v-click
    >
      <div class="metric-value">{{ metric.value }}</div>
      <div class="metric-label">{{ metric.label }}</div>
      <div v-if="metric.description" class="metric-description">
        {{ metric.description }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Metric {
  value: string
  label: string
  description?: string
  class?: string
}

defineProps<{
  metrics: Metric[]
}>()
</script>

<style scoped>
.metrics-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 2rem 0;
}

.metric-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.metric-value {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.metric-label {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
}

.metric-description {
  font-size: 0.9rem;
  opacity: 0.7;
}
</style>