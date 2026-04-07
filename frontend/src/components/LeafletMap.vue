<script setup>
import L from 'leaflet'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const DEFAULT_CENTER = [28.2282, 112.9388]
const CHINESE_TILE_URL = 'https://map.geoq.cn/ArcGIS/rest/services/ChinaOnlineCommunity/MapServer/tile/{z}/{y}/{x}'

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
      <div class="map-popup__line">综合评分：${point.total_score ?? '-'}</div>
      <div class="map-popup__line">评级：${point.level || '-'}</div>
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
      radius: 9,
      color: '#23303b',
      weight: 1.5,
      fillColor: point.marker_color || '#c29b63',
      fillOpacity: 0.95
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
    zoomControl: false,
    attributionControl: true
  }).setView(DEFAULT_CENTER, 10)

  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance)
  mapInstance.attributionControl.setPrefix(false)

  L.tileLayer(CHINESE_TILE_URL, {
    maxZoom: 18,
    attribution: '&copy; GeoQ 中文地图'
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
  background: #e2e7ee;
  font-family: var(--font-main);
}

:deep(.leaflet-control-zoom a) {
  background: rgba(255, 255, 255, 0.96);
  color: #1f2730;
  border-bottom-color: #d2d9e2;
}

:deep(.leaflet-control-zoom a:hover) {
  background: #f7f9fb;
}

:deep(.leaflet-control-attribution) {
  background: rgba(255, 255, 255, 0.92);
  color: #66717e;
}

:deep(.leaflet-popup-content-wrapper) {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #d7dee7;
  color: #1f2730;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.18);
}

:deep(.leaflet-popup-tip) {
  background: rgba(255, 255, 255, 0.96);
}

:deep(.leaflet-popup-content) {
  margin: 14px 16px;
}

:deep(.map-popup) {
  min-width: 188px;
}

:deep(.map-popup__title) {
  margin-bottom: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #1f2730;
}

:deep(.map-popup__line) {
  color: #4f5966;
  line-height: 1.8;
  font-size: 13px;
}

:deep(.map-popup__link) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
  margin-top: 12px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid #d7dee7;
  background: #f5f7fa;
  color: #1f2730;
  text-decoration: none;
  font-size: 13px;
}

:deep(.map-popup__link:hover) {
  background: #eceff4;
}
</style>
