<script setup>
import L from 'leaflet'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  points: {
    type: Array,
    default: () => []
  },
  height: {
    type: String,
    default: '340px'
  }
})

const mapRef = ref(null)
let mapInstance = null
let markerLayer = null

function buildPopup(point) {
  return `
    <div style="min-width: 180px;">
      <div style="font-weight: 600; margin-bottom: 6px;">${point.location_name || '未命名点位'}</div>
      <div>任务编号：${point.task_no || '-'}</div>
      <div>评级：${point.level || '-'}</div>
      <div>评分：${point.total_score ?? '-'}</div>
      <div style="margin-top: 8px;">
        <a href="#/tasks/${point.task_id}" style="color:#2563eb;text-decoration:none;">查看详情</a>
      </div>
    </div>
  `
}

function renderPoints() {
  if (!mapInstance || !markerLayer) return
  markerLayer.clearLayers()

  if (!props.points.length) {
    mapInstance.setView([31.23, 121.47], 10)
    return
  }

  const bounds = []
  props.points.forEach((point) => {
    if (point.latitude == null || point.longitude == null) return
    const latlng = [point.latitude, point.longitude]
    bounds.push(latlng)
    const marker = L.circleMarker(latlng, {
      radius: 8,
      color: point.marker_color || '#2563eb',
      fillColor: point.marker_color || '#2563eb',
      fillOpacity: 0.78,
      weight: 2
    })
    marker.bindPopup(buildPopup(point))
    marker.addTo(markerLayer)
  })

  if (bounds.length === 1) {
    mapInstance.setView(bounds[0], 12)
  } else if (bounds.length > 1) {
    mapInstance.fitBounds(bounds, { padding: [20, 20] })
  }
}

onMounted(async () => {
  await nextTick()
  mapInstance = L.map(mapRef.value, {
    zoomControl: true,
    attributionControl: true
  }).setView([31.23, 121.47], 10)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap'
  }).addTo(mapInstance)

  markerLayer = L.layerGroup().addTo(mapInstance)
  renderPoints()
})

watch(
  () => props.points,
  async () => {
    await nextTick()
    renderPoints()
  },
  { deep: true }
)

onBeforeUnmount(() => {
  mapInstance?.remove()
})
</script>

<template>
  <div ref="mapRef" :style="{ width: '100%', height }" class="map-panel"></div>
</template>
