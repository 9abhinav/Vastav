import api from './api';

export const TrafficService = {
  // Health & Stats
  getHealth: () => api.get('/health').then(r => r.data),
  getStats: () => api.get('/statistics').then(r => r.data),

  // Vehicles
  getVehicles: (params) => api.get('/vehicles', { params }).then(r => r.data),
  getVehicle: (id) => api.get(`/vehicles/${id}`).then(r => r.data),

  // Violations
  getViolations: (params) => api.get('/violations', { params }).then(r => r.data),
  getViolation: (id) => api.get(`/violations/${id}`).then(r => r.data),
  updateViolation: (id, data) => api.put(`/violations/${id}`, data).then(r => r.data),
  deleteViolation: (id) => api.delete(`/violations/${id}`).then(r => r.data),
  getViolationsCsvUrl: () => '/api/violations/export/csv',

  // Settings & Calibration
  getSettings: () => api.get('/settings').then(r => r.data),
  updateSettings: (data) => api.put('/settings', data).then(r => r.data),
  setTrafficLight: (state) => api.post(`/settings/traffic-light?state=${state}`).then(r => r.data),

  // Video stream control
  getVideoStatus: () => api.get('/video/status').then(r => r.data),
  startVideo: (data) => api.post('/video/start', data).then(r => r.data),
  stopVideo: () => api.post('/video/stop').then(r => r.data),
  pauseVideo: () => api.post('/video/pause').then(r => r.data),
  resumeVideo: () => api.post('/video/resume').then(r => r.data),
  uploadVideo: (formData) => api.post('/video/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(r => r.data),

  // Cameras
  getCameras: () => api.get('/cameras').then(r => r.data),
};
