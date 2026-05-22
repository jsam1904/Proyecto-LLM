import axios from 'axios'

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

// ── Response interceptor: redirige al login si el token EXPIRA ────
// ⚠️  NO redirigir si la propia petición de login falla con 401
//     (credenciales incorrectas). En ese caso dejamos que el
//     componente maneje el error y muestre el mensaje al usuario.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes('/api/users/login') ||
                           error.config?.url?.includes('/api/users/register')

    if (error.response?.status === 401 && !isLoginRequest) {
      // Token expirado o inválido en una ruta protegida → forzar logout
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default api
