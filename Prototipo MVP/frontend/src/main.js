import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import Dashboard   from './views/Dashboard.vue'
import StudyPlan   from './views/StudyPlan.vue'
import AIAssistant from './views/AIAssistant.vue'
import Progress    from './views/Progress.vue'
import Login       from './views/Login.vue'
import './assets/main.css'

// ── Rutas ─────────────────────────────────────────────────────────
const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/',          component: Dashboard,   meta: { public: false } },
  { path: '/plan',      component: StudyPlan,   meta: { public: false } },
  { path: '/assistant', component: AIAssistant, meta: { public: false } },
  { path: '/progress',  component: Progress,    meta: { public: false } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Auth guard ────────────────────────────────────────────────────
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')
  const isPublic = to.meta.public === true

  // Ruta protegida sin token → redirigir al login
  if (!isPublic && !token) {
    return { path: '/login', replace: true }
  }

  // Ya tiene sesión e intenta ir al login → redirigir al dashboard
  if (to.path === '/login' && token) {
    return { path: '/', replace: true }
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
