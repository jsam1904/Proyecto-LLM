import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api.js'

export const useAuthStore = defineStore('auth', () => {
  // ── Estado ────────────────────────────────────────────────
  const token = ref(localStorage.getItem('token') || null)
  const user  = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // ── Getters ───────────────────────────────────────────────
  const isLoggedIn = computed(() => !!token.value)
  const userId     = computed(() => user.value?.id ?? null)
  const userName   = computed(() => user.value?.name ?? '')
  const userInitials = computed(() => {
    if (!user.value?.name) return '?'
    return user.value.name
      .split(' ')
      .slice(0, 2)
      .map((w) => w[0].toUpperCase())
      .join('')
  })

  // ── Acciones ──────────────────────────────────────────────
  async function login(email, password) {
    // FastAPI OAuth2PasswordRequestForm requiere application/x-www-form-urlencoded
    // URLSearchParams genera ese formato automáticamente con axios
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)

    const { data } = await api.post('/api/users/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })

    token.value = data.access_token
    user.value  = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
  }

  async function register(name, email, password) {
    await api.post('/api/users/register', { name, email, password })
    await login(email, password)
  }

  function logout() {
    token.value = null
    user.value  = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isLoggedIn,
    userId,
    userName,
    userInitials,
    login,
    register,
    logout,
  }
})
