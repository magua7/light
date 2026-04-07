import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/api',
  timeout: 15000
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
    ElMessage.error(detail || error.message || '网络请求失败')
    return Promise.reject(error)
  }
)

export default service
