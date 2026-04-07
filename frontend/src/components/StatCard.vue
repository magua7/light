<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  value: {
    type: [String, Number],
    default: '-'
  },
  description: {
    type: String,
    default: ''
  },
  accent: {
    type: String,
    default: '#f1ede6'
  }
})
</script>

<template>
  <div class="stat-card">
    <div class="stat-bar" :style="{ background: accent }"></div>
    <div class="stat-label">{{ title }}</div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-desc">{{ description }}</div>
  </div>
</template>
