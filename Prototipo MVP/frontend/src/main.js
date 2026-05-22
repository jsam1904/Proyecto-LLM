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
  { path: '/',          component: Dashboard   },
  { path: '/plan',      component: StudyPlan   },
  { path: '/assistant', component: AIAssistant },
  { path: '/progress',  component: Progress    },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Auth guard: redirige al login si no hay token ─────────────────
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    return '/login'
  }
  // Si ya está logueado y va a /login, redirigir al dashboard
  if (to.path === '/login' && token) {
    return '/'
  }
})

// ── App ───────────────────────────────────────────────────────────
const pinia = createPinia()
const app   = createApp(App)

app.use(pinia)
app.use(router)
app.mount('#app')
