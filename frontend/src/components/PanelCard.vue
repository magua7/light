<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="panel-card">
    <div v-if="title || $slots.extra" class="panel-head">
      <div class="panel-title">{{ title }}</div>
      <div class="panel-extra">
        <slot name="extra" />
      </div>
    </div>
    <div class="panel-body">
      <slot />
    </div>
  </div>
</template>
