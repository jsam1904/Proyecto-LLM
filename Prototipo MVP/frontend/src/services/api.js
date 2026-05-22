import axios from 'axios'

// Sin baseURL: las peticiones a /api/... se envían a Vite dev server
// que las proxea a http://backend:8000 (nombre del servicio en Docker).
// Para desarrollo local sin Docker, cambia target en vite.config.js a
// http://localhost:8000
const api = axios.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor: adjunta el JWT en cada petición ──────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: redirige al login si el token expira ────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
