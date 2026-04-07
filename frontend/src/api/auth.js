import http from './http'

export const registerAccount = (payload) => http.post('/auth/register', payload)

export const loginAccount = (payload) => http.post('/auth/login', payload)

export const fetchCurrentUser = () => http.get('/auth/me')

export const logoutAccount = () => http.post('/auth/logout')
