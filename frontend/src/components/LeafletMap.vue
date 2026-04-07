<script setup>
import L from 'leaflet'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const DEFAULT_CENTER = [28.2282, 112.9388]

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
    <div class="map-popup">
      <div class="map-popup__title">${point.location_name || '未命名点位'}</div>
      <div class="map-popup__line">任务编号：${point.task_no || '-'}</div>
      <div class="map-popup__line">评级：${point.level || '-'}</div>
      <div class="map-popup__line">评分：${point.total_score ?? '-'}</div>
      <a href="#/tasks/${point.task_id}" class="map-popup__link">查看报告</a>
    </div>
  `
}

function renderPoints() {
  if (!mapInstance || !markerLayer) return
  markerLayer.clearLayers()

  if (!props.points.length) {
    mapInstance.setView(DEFAULT_CENTER, 10)
    return
  }

  const bounds = []
  props.points.forEach((point) => {
    if (point.latitude == null || point.longitude == null) return
    const latlng = [point.latitude, point.longitude]
    bounds.push(latlng)
    const marker = L.circleMarker(latlng, {
      radius: 8,
      color: point.marker_color || '#d2ccc1',
      fillColor: point.marker_color || '#d2ccc1',
      fillOpacity: 0.82,
      weight: 2
    })
    marker.bindPopup(buildPopup(point))
    marker.addTo(markerLayer)
  })

  if (bounds.length === 1) {
    mapInstance.setView(bounds[0], 12)
  } else if (bounds.length > 1) {
    mapInstance.fitBounds(bounds, { padding: [24, 24] })
  }
}

onMounted(async () => {
  await nextTick()
  mapInstance = L.map(mapRef.value, {
    zoomControl: true,
    attributionControl: true
  }).setView(DEFAULT_CENTER, 10)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap &copy; CARTO'
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

<style scoped>
:deep(.leaflet-container) {
  background: #090a0c;
  font-family: var(--font-main);
}

:deep(.leaflet-control-zoom a) {
  background: rgba(17, 19, 21, 0.96);
  color: var(--text-main);
  border-bottom-color: rgba(255, 255, 255, 0.08);
}

:deep(.leaflet-control-attribution) {
  background: rgba(11, 12, 15, 0.78);
  color: var(--text-muted);
}

:deep(.leaflet-popup-content-wrapper) {
  background: rgba(17, 19, 21, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-main);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.32);
}

:deep(.leaflet-popup-tip) {
  background: rgba(17, 19, 21, 0.96);
}

:deep(.leaflet-popup-content) {
  margin: 14px 16px;
}

:deep(.map-popup) {
  min-width: 180px;
}

:deep(.map-popup__title) {
  margin-bottom: 8px;
  font-size: 15px;
  font-weight: 700;
}

:deep(.map-popup__line) {
  color: var(--text-sub);
  line-height: 1.8;
  font-size: 13px;
}

:deep(.map-popup__link) {
  display: inline-block;
  margin-top: 10px;
  color: var(--accent-main);
  text-decoration: none;
}
</style>
