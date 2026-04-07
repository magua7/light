import http from './http'

const AUTH_TIMEOUT = 8000
const HEALTH_TIMEOUT = 3000

export const registerAccount = (payload) =>
  http.post('/auth/register', payload, {
    timeout: AUTH_TIMEOUT
  })

export const loginAccount = (payload) =>
  http.post('/auth/login', payload, {
    timeout: AUTH_TIMEOUT
  })

export const fetchCurrentUser = (options = {}) =>
  http.get('/auth/me', {
    timeout: AUTH_TIMEOUT,
    silentError: options.silentError ?? false,
    skipAuthCleanup: options.skipAuthCleanup ?? false
  })

export const logoutAccount = () =>
  http.post('/auth/logout', null, {
    timeout: AUTH_TIMEOUT
  })

export const checkBackendHealth = () =>
  http.get('/health', {
    timeout: HEALTH_TIMEOUT,
    silentError: true,
    skipAuthToken: true,
    skipAuthCleanup: true
  })
