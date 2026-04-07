<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="panel-card">
    <div v-if="title || subtitle || $slots.extra" class="panel-head">
      <div>
        <div v-if="title" class="panel-title">{{ title }}</div>
        <div v-if="subtitle" class="panel-subtitle">{{ subtitle }}</div>
      </div>
      <div class="panel-extra">
        <slot name="extra" />
      </div>
    </div>
    <div class="panel-body">
      <slot />
    </div>
  </div>
</template>
