<template>
  <div class="view">
    <header class="view-header">
      <div>
        <h1>Dashboard</h1>
        <p class="subtitle">Bienvenida, María. Tienes examen de Cálculo en 3 días.</p>
      </div>
      <span class="date-badge">{{ today }}</span>
    </header>

    <!-- Metric cards -->
    <section class="metrics">
      <MetricCard label="Horas esta semana" :value="14.5" unit="h" trend="+2.3h vs semana anterior" />
      <MetricCard label="Tareas completadas" value="8/12" trend="67% completado" />
      <MetricCard label="Racha actual" :value="5" unit=" días" trend="Mejor racha: 9 días" />
      <MetricCard label="Próximo examen" value="3 días" trend="Cálculo II — Lunes" />
    </section>

    <div class="two-col">
      <!-- Tasks -->
      <div class="card">
        <h2 class="card-title">Tareas de hoy</h2>
        <div class="task-list">
          <TaskItem
            v-for="task in tasks"
            :key="task.id"
            :task="task"
            @toggle="toggleTask(task.id)"
          />
        </div>
        <button class="add-task-btn" @click="showAddTask = true">+ Agregar tarea</button>
      </div>

      <!-- Activity heatmap -->
      <div class="card">
        <h2 class="card-title">Actividad semanal</h2>
        <WeekHeatmap :data="weekData" />
      </div>
    </div>

    <!-- AI suggestion banner -->
    <div class="ai-banner">
      <div class="ai-banner-icon">
        <svg viewBox="0 0 16 16" fill="#0F6E56" width="16" height="16">
          <path d="M8 2L10 7H15L11 10L13 15L8 12L3 15L5 10L1 7H6Z"/>
        </svg>
      </div>
      <div class="ai-banner-text">
        <strong>Sugerencia del Asistente IA</strong>
        <p>Tienes examen de Cálculo en 3 días. Recomiendo dedicar 2h hoy a ejercicios de integrales definidas antes de las 8pm.</p>
      </div>
      <router-link to="/assistant" class="ai-banner-btn">Consultar ↗</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import MetricCard from '../components/MetricCard.vue'
import TaskItem from '../components/TaskItem.vue'
import WeekHeatmap from '../components/WeekHeatmap.vue'

const today = computed(() => new Date().toLocaleDateString('es-GT', { weekday: 'long', day: 'numeric', month: 'long' }))

const tasks = ref([
  { id: 1, text: 'Leer cap. 5 de BD relacionales', tag: 'BD', done: true },
  { id: 2, text: 'Resolver ejercicios de integrales', tag: 'Cálculo', done: false },
  { id: 3, text: 'Implementar CRUD en Python/Flask', tag: 'Prog', done: false },
  { id: 4, text: 'Revisar notas de IA — modelos LLM', tag: 'IA', done: true },
])

const weekData = ref([
  { day: 'L', hours: [2, 3, 1] },
  { day: 'M', hours: [1, 2, 0] },
  { day: 'Mi', hours: [3, 3, 2] },
  { day: 'J', hours: [2, 1, 2] },
  { day: 'V', hours: [1, 3, 1] },
  { day: 'S', hours: [0, 1, 0] },
  { day: 'D', hours: [0, 0, 0] },
])

function toggleTask(id) {
  const t = tasks.value.find(t => t.id === id)
  if (t) t.done = !t.done
}
</script>

<style scoped>
.view {
  padding: 2rem 2rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 1100px;
  min-height: 100%;
  box-sizing: border-box;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

h1 {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 3px;
}

.date-badge {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-hover);
  padding: 5px 12px;
  border-radius: 20px;
  text-transform: capitalize;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.add-task-btn {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-secondary);
  background: none;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius-sm);
  padding: 7px 12px;
  width: 100%;
  cursor: pointer;
  transition: background 0.15s;
}

.add-task-btn:hover { background: var(--bg-hover); }

.ai-banner {
  background: var(--accent-light);
  border: 1px solid rgba(29,158,117,0.2);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-banner-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(29,158,117,0.2);
}

.ai-banner-text {
  flex: 1;
  font-size: 13px;
  color: var(--accent-dark);
}

.ai-banner-text strong { display: block; margin-bottom: 2px; }
.ai-banner-text p { font-weight: 400; opacity: 0.85; }

.ai-banner-btn {
  font-size: 12px;
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  background: white;
  border: 1px solid rgba(29,158,117,0.3);
  color: var(--accent-dark);
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.15s;
}

.ai-banner-btn:hover { background: var(--accent-light); }
</style>
