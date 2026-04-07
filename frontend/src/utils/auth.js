const TOKEN_KEY = 'light-inspector-token'
const USER_KEY = 'light-inspector-user'

export function isLoggedIn() {
  return Boolean(getToken())
}

export function getToken() {
  if (typeof window === 'undefined') return ''
  return window.localStorage.getItem(TOKEN_KEY) || ''
}

export function getCurrentUser() {
  if (typeof window === 'undefined') return null
  const raw = window.localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function persistAuth(token, user) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(TOKEN_KEY, token)
  window.localStorage.setItem(USER_KEY, JSON.stringify(user || null))
}

export function setCurrentUser(user) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(USER_KEY, JSON.stringify(user || null))
}

export function clearAuth() {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem(TOKEN_KEY)
  window.localStorage.removeItem(USER_KEY)
}

export function getLoginUser() {
  return getCurrentUser()?.username || ''
}
