import http from './http'

const AUTH_TIMEOUT = 8000

export const registerAccount = (payload) =>
  http.post('/auth/register', payload, {
    timeout: AUTH_TIMEOUT
  })

export const loginAccount = (payload) =>
  http.post('/auth/login', payload, {
    timeout: AUTH_TIMEOUT
  })

export const fetchCurrentUser = () =>
  http.get('/auth/me', {
    timeout: AUTH_TIMEOUT
  })

export const logoutAccount = () =>
  http.post('/auth/logout', null, {
    timeout: AUTH_TIMEOUT
  })
