export const directionMap = {
  east: '东向',
  south: '南向',
  west: '西向',
  north: '北向'
}

export const typeMap = {
  ad_light: '广告光源',
  up_light: '上射光源',
  move_light: '动态光源',
  stay_light: '常亮光源'
}

export const levelTagMap = {
  优: 'success',
  良: 'success',
  中: 'warning',
  较差: 'danger',
  差: 'danger'
}

export const levelColorMap = {
  优: '#4caf50',
  良: '#8bc34a',
  中: '#ffb300',
  较差: '#ff7043',
  差: '#e53935'
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
