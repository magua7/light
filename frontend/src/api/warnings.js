import http from './http'

export const fetchWarningList = () => http.get('/warnings/list')

export const updateWarningStatus = (id, processStatus) =>
  http.put(`/warnings/${id}/status`, {
    process_status: processStatus
  })
