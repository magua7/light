import http from './http'

export const fetchOverview = () => http.get('/dashboard/overview')
export const fetchTrend = () => http.get('/dashboard/trend')
export const fetchTypeDistribution = () => http.get('/dashboard/type-distribution')
export const fetchMapPoints = () => http.get('/dashboard/map-points')
