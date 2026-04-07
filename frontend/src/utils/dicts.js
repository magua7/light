export const directionMap = {
  east: '图片1',
  south: '图片2',
  west: '图片3',
  north: '图片4'
}

export const imageSlotOptions = [
  { key: 'east', title: '图片1' },
  { key: 'south', title: '图片2' },
  { key: 'west', title: '图片3' },
  { key: 'north', title: '图片4' }
]

export const typeMap = {
  ad_light: '广告光源',
  up_light: '上射光源',
  move_light: '动态光源',
  stay_light: '常亮光源'
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
