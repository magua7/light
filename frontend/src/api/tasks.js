import http from './http'

export const createTask = (formData) =>
  http.post('/tasks/create', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

export const fetchTaskDetail = (taskId) => http.get(`/tasks/${taskId}`)

export const fetchTaskList = (params) => http.get('/tasks/list', { params })
