<script setup>
import L from 'leaflet'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const DEFAULT_CENTER = [28.2282, 112.9388]
const TILE_PROVIDERS = [
  {
    name: '高德中文地图',
    url: 'https://wprd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&style=7&x={x}&y={y}&z={z}',
    options: {
      maxZoom: 18,
      subdomains: ['1', '2', '3', '4']
    }
  },
  {
    name: '高德中文备用',
    url: 'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
    options: {
      maxZoom: 18,
      subdomains: ['1', '2', '3', '4']
    }
  },
  {
    name: 'OpenStreetMap',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    options: {
      maxZoom: 19,
      subdomains: ['a', 'b', 'c']
    }
  }
]
const TILE_ERROR_THRESHOLD = 8

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
let baseLayer = null
let activeProviderIndex = 0
let tileErrorCount = 0
let resizeObserver = null
let resizeTimer = null

function handleWindowResize() {
  scheduleInvalidateSize(80)
}

function cleanupBaseLayer() {
  if (!baseLayer) return
  baseLayer.off('tileerror', handleTileError)
  baseLayer.off('load', handleTileLoad)
  baseLayer.remove()
  baseLayer = null
}

function handleTileError() {
  tileErrorCount += 1
  if (tileErrorCount < TILE_ERROR_THRESHOLD || activeProviderIndex >= TILE_PROVIDERS.length - 1) {
    return
  }
  setBaseLayer(activeProviderIndex + 1)
}

function handleTileLoad() {
  scheduleInvalidateSize(60)
}

function setBaseLayer(index = 0) {
  if (!mapInstance) return
  cleanupBaseLayer()

  activeProviderIndex = index
  tileErrorCount = 0
  const provider = TILE_PROVIDERS[index]

  baseLayer = L.tileLayer(provider.url, {
    ...provider.options,
    attribution: `&copy; ${provider.name}`
  })
  baseLayer.on('tileerror', handleTileError)
  baseLayer.on('load', handleTileLoad)
  baseLayer.addTo(mapInstance)
}

function scheduleInvalidateSize(delay = 120) {
  if (!mapInstance) return
  window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(() => {
    mapInstance?.invalidateSize({ pan: false, animate: false })
  }, delay)
}

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

  setBaseLayer(0)
  markerLayer = L.layerGroup().addTo(mapInstance)
  renderPoints()
  scheduleInvalidateSize(180)

  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      scheduleInvalidateSize(80)
    })
    resizeObserver.observe(mapRef.value)
  }

  window.addEventListener('resize', handleWindowResize)
})

watch(
  () => props.points,
  async () => {
    await nextTick()
    renderPoints()
    scheduleInvalidateSize(120)
  },
  { deep: true }
)

watch(
  () => props.height,
  async () => {
    await nextTick()
    scheduleInvalidateSize(120)
  }
)

onBeforeUnmount(() => {
  window.clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleWindowResize)
  resizeObserver?.disconnect()
  cleanupBaseLayer()
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
