import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 15000,
})

// Attach stored token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('agro_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('agro_token')
      localStorage.removeItem('agro_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login:    (data) => api.post('/auth/login', data),
}

// ─── Farm ─────────────────────────────────────────────────────────────────────
export const farmAPI = {
  saveInput:    (data) => api.post('/farm/input', data),
  getLatest:    ()     => api.get('/farm/latest'),
}

// ─── Prediction ───────────────────────────────────────────────────────────────
export const predictionAPI = {
  predict:     (data) => api.post('/prediction/predict', data),
  selectCrop:  (data) => api.post('/prediction/select-crop', data),
}

// ─── Timeline ─────────────────────────────────────────────────────────────────
export const timelineAPI = {
  getActive:      ()                          => api.get('/timeline/active'),
  getAll:         ()                          => api.get('/timeline/all'),
  completeTask:   (timelineId, day)           => api.patch(`/timeline/${timelineId}/task/${day}/complete`),
}

// ─── Notifications ────────────────────────────────────────────────────────────
export const notifAPI = {
  getHistory:     ()  => api.get('/notifications/history'),
  triggerCheck:   ()  => api.post('/notifications/trigger-daily'),
}

// ─── Chat ─────────────────────────────────────────────────────────────────────
export const chatAPI = {
  send: (message, language = 'en') => api.post('/chat/message', { message, language }),
}
