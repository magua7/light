import axios from 'axios'
import { ElMessage } from 'element-plus'

import { clearAuth, getToken } from '../utils/auth'

const service = axios.create({
  baseURL: '/api',
  timeout: 15000
})

service.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

service.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload.code !== 0) {
      ElMessage.error(payload.message || '请求失败')
      return Promise.reject(new Error(payload.message || 'request error'))
    }
    return payload.data
  },
  (error) => {
    const detail = error.response?.data?.detail
    if (error.response?.status === 401) {
      clearAuth()
    }
    ElMessage.error(detail || error.message || '网络请求失败')
    return Promise.reject(error)
  }
)

export default service
