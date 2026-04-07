import axios from 'axios'
import { ElMessage } from 'element-plus'

import { clearAuth, getToken } from '../utils/auth'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://127.0.0.1:8000/api' : '/api')

function buildErrorMessage(error) {
  const requestUrl = error.config?.url || ''
  const isLoginRequest = requestUrl.includes('/auth/login')

  if (error.code === 'ECONNABORTED') {
    return isLoginRequest
      ? '登录接口请求超时，请检查后端是否正常启动。'
      : '接口请求超时，请稍后重试。'
  }

  if (!error.response) {
    return isLoginRequest
      ? '无法连接到后端服务，请确认后端已启动并监听 http://127.0.0.1:8000。'
      : '无法连接到后端服务，请检查网络或服务状态。'
  }

  const detail = error.response?.data?.detail
  if (detail) return detail

  if (error.response.status === 401) {
    return isLoginRequest ? '用户名或密码错误。' : '当前登录状态已失效，请重新登录。'
  }

  if (error.response.status >= 500) {
    return '服务器异常，请查看后端日志。'
  }

  return error.message || '网络请求失败'
}

const service = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000
})

service.interceptors.request.use((config) => {
  const token = getToken()
  if (token && !config.skipAuthToken) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

service.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload.code !== 0) {
      if (!response.config?.silentError) {
        ElMessage.error(payload.message || '请求失败')
      }
      return Promise.reject(new Error(payload.message || 'request error'))
    }
    return payload.data
  },
  (error) => {
    if (error.response?.status === 401 && !error.config?.skipAuthCleanup) {
      clearAuth()
    }
    if (!error.config?.silentError) {
      ElMessage.error(buildErrorMessage(error))
    }
    return Promise.reject(error)
  }
)

export default service
