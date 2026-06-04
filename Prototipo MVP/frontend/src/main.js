import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import Dashboard   from './views/Dashboard.vue'
import StudyPlan   from './views/StudyPlan.vue'
import AIAssistant from './views/AIAssistant.vue'
import Progress    from './views/Progress.vue'
import Repaso      from './views/Repaso.vue'
import Login       from './views/Login.vue'
import './assets/main.css'
import 'katex/dist/katex.min.css'

// ── Rutas ─────────────────────────────────────────────────────────
const routes = [
  {
    path: '/',
    redirect: () => {
      const token = localStorage.getItem('token')
      return token ? '/dashboard' : '/login'
    },
  },
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/dashboard', component: Dashboard,   meta: { public: false } },
  { path: '/plan',      component: StudyPlan,   meta: { public: false } },
  { path: '/assistant', component: AIAssistant, meta: { public: false } },
  { path: '/progress',  component: Progress,    meta: { public: false } },
  { path: '/repaso',    component: Repaso,       meta: { public: false } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Auth guard ────────────────────────────────────────────────────
function isTokenValid(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 > Date.now()
  } catch {
    return false
  }
}

router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')
  const validToken = token && isTokenValid(token)
  const isPublic = to.meta.public === true

  if (!validToken && token) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Ruta protegida sin token válido → redirigir al login
  if (!isPublic && !validToken) {
    return { path: '/login', replace: true }
  }

  // Ya tiene sesión válida e intenta ir al login → redirigir al dashboard
  if (to.path === '/login' && validToken) {
    return { path: '/dashboard', replace: true }
  }

  // En cualquier otro caso permitir la navegación
  return true
})

// ── App ───────────────────────────────────────────────────────────
const pinia = createPinia()
const app   = createApp(App)

app.use(pinia)
app.use(router)
app.mount('#app')
