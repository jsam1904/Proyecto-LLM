import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import StudyPlan from './views/StudyPlan.vue'
import AIAssistant from './views/AIAssistant.vue'
import Progress from './views/Progress.vue'
import './assets/main.css'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/plan', component: StudyPlan },
  { path: '/assistant', component: AIAssistant },
  { path: '/progress', component: Progress },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
