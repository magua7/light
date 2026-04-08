export const BRAND_FULL_NAME = '净光物联城市光污染多模态感知监测与智能评级系统'
export const BRAND_SHORT_NAME = '净光物联'
export const BRAND_NAV_NAME = '城市光污染监测'
export const BRAND_SLOGAN = '少一分多余光亮，多一分星空浪漫'

export const analysisDirections = ['east', 'south', 'west', 'north']

export const directionMap = {
  east: '图片1',
  south: '图片2',
  west: '图片3',
  north: '图片4'
}

export const imageSlotOptions = analysisDirections.map((key) => ({
  key,
  title: directionMap[key]
}))

export const typeMap = {
  ad_light: '广告光源',
  up_light: '上射光源',
  move_light: '动态光源',
  stay_light: '静态光源'
}

export const levelTagMap = {
  优: 'success',
  良: 'info',
  中: 'warning',
  较差: 'danger',
  差: 'danger'
}

export const levelColorMap = {
  优: '#6d9776',
  良: '#8f9cac',
  中: '#c29b63',
  较差: '#bb735c',
  差: '#944d44'
}

export const chartPalette = {
  bright: '#f5f7fa',
  light: '#d6dde6',
  mid: '#8f9cac',
  muted: '#707b88',
  warning: '#c29b63',
  danger: '#bb735c',
  success: '#6d9776'
}

export function buildDocumentTitle(pageTitle = '') {
  return pageTitle ? `${pageTitle} - ${BRAND_FULL_NAME}` : BRAND_FULL_NAME
}

export function formatDirection(value) {
  return directionMap[value] || value || '-'
}

export function formatType(value) {
  return typeMap[value] || value || '-'
}

export function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (num) => `${num}`.padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

export function formatImageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return path
}

export function formatCoordinate(longitude, latitude) {
  if (longitude == null || latitude == null) return '-'
  return `${Number(longitude).toFixed(3)}, ${Number(latitude).toFixed(3)}`
}

export function formatCoordinateDisplay(longitude, latitude) {
  if (longitude == null || latitude == null) return '-'
  const lon = Number(longitude)
  const lat = Number(latitude)
  if (!Number.isFinite(lon) || !Number.isFinite(lat)) return '-'
  const lonSuffix = lon >= 0 ? 'E' : 'W'
  const latSuffix = lat >= 0 ? 'N' : 'S'
  return `经度 ${Math.abs(lon).toFixed(2)}${lonSuffix}，纬度 ${Math.abs(lat).toFixed(2)}${latSuffix}`
}
