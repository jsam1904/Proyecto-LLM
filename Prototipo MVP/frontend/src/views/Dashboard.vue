<template>
  <div class="view">
    <header class="view-header">
      <div>
        <h1>Dashboard</h1>
        <p class="subtitle">
          Bienvenido, {{ authStore.userName }}.
          <span v-if="nextExam">
            Tienes examen de {{ nextExam.subject }} en {{ nextExam.days_remaining }} día(s).
          </span>
        </p>
      </div>
      <span class="date-badge">{{ today }}</span>
    </header>

    <!-- Cargando -->
    <div v-if="loading" class="loading-row">
      <span class="spinner-lg"></span> Cargando...
    </div>

    <template v-else>
      <!-- Metric cards -->
      <section class="metrics">
        <MetricCard
          label="Tareas pendientes"
          :value="pendingTasks.length"
          unit=" pendientes"
          :trend="`${doneTasks.length} completadas`"
        />
        <MetricCard
          label="Completadas hoy"
          :value="todayDone"
          unit=" hoy"
          trend="Tareas finalizadas hoy"
        />
        <MetricCard
          label="Total tareas"
          :value="tasks.length"
          trend="En total registradas"
        />
        <MetricCard
          v-if="nextExam"
          label="Próximo examen"
          :value="`${nextExam.days_remaining} días`"
          :trend="nextExam.subject"
        />
        <MetricCard
          v-else
          label="Próximo examen"
          value="—"
          trend="Sin exámenes registrados"
        />
      </section>

      <!-- AI suggestion banner -->
      <div class="ai-banner">
        <div class="ai-banner-icon">
          <svg viewBox="0 0 16 16" fill="#0F6E56" width="16" height="16">
            <path d="M8 2L10 7H15L11 10L13 15L8 12L3 15L5 10L1 7H6Z"/>
          </svg>
        </div>
        <div class="ai-banner-text">
          <strong>Sugerencia del Asistente IA</strong>
          <p v-if="nextExam">
            Tienes examen de {{ nextExam.subject }} en {{ nextExam.days_remaining }} día(s).
            Te recomiendo hacer un repaso intensivo. ¡El Asistente IA puede ayudarte!
          </p>
          <p v-else-if="pendingTasks.length">
            Tienes {{ pendingTasks.length }} tarea(s) pendiente(s). ¡El Asistente IA puede ayudarte a planificar!
          </p>
          <p v-else>
            ¡Todo al día! Consulta al Asistente IA para generar tu plan de estudio semanal.
          </p>
        </div>
        <router-link to="/assistant" class="ai-banner-btn">Consultar ↗</router-link>
      </div>

      <div class="two-col">
        <!-- Tasks -->
        <div class="card">
          <div class="card-title-row">
            <h2 class="card-title">Mis tareas</h2>
            <div class="filter-row">
              <button :class="['filter-btn', { active: filter === 'all' }]"    @click="filter = 'all'">Todas</button>
              <button :class="['filter-btn', { active: filter === 'pending' }]" @click="filter = 'pending'">Pendientes</button>
              <button :class="['filter-btn', { active: filter === 'done' }]"   @click="filter = 'done'">Completadas</button>
            </div>
          </div>

          <div v-if="filteredTasks.length" class="task-list">
            <TaskItem
              v-for="task in filteredTasks"
              :key="task.id"
              :task="task"
              @toggle="toggleTask(task)"
              @delete="deleteTask(task.id)"
            />
          </div>
          <p v-else class="empty-msg">No hay tareas en esta categoría.</p>

          <button class="add-task-btn" @click="showModal = true">+ Agregar tarea</button>
        </div>

        <!-- Activity heatmap -->
        <div class="card">
          <h2 class="card-title">Actividad semanal</h2>
          <WeekHeatmap :data="weekData" />
        </div>
      </div>
    </template>

    <!-- Modal agregar tarea -->
    <AddTaskModal
      v-if="showModal"
      @close="showModal = false"
      @created="onTaskCreated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import MetricCard    from '../components/MetricCard.vue'
import TaskItem      from '../components/TaskItem.vue'
import WeekHeatmap   from '../components/WeekHeatmap.vue'
import AddTaskModal  from '../components/AddTaskModal.vue'
import api           from '../services/api.js'
import { useAuthStore } from '../stores/auth.js'

const authStore = useAuthStore()
const loading   = ref(true)
const tasks     = ref([])
const nextExam  = ref(null)
const showModal = ref(false)
const filter    = ref('all')

const today = computed(() =>
  new Date().toLocaleDateString('es-GT', { weekday: 'long', day: 'numeric', month: 'long' })
)

// ── Tareas filtradas ──────────────────────────────────────────────
const pendingTasks = computed(() => tasks.value.filter(t => !t.done))
const doneTasks    = computed(() => tasks.value.filter(t => t.done))

const todayDone = computed(() => {
  const today = new Date().toDateString()
  return doneTasks.value.filter(t => {
    return t.updated_at && new Date(t.updated_at).toDateString() === today
  }).length
})

const filteredTasks = computed(() => {
  if (filter.value === 'pending') return pendingTasks.value
  if (filter.value === 'done')    return doneTasks.value
  return tasks.value
})

// ── Heatmap (días de la semana con conteo de tareas completadas) ──
const weekData = computed(() => {
  const days = ['L', 'M', 'Mi', 'J', 'V', 'S', 'D']
  return days.map((day, i) => {
    const count = tasks.value.filter(t => {
      const d = t.created_at ? new Date(t.created_at).getDay() : -1
      const adjusted = d === 0 ? 6 : d - 1  // 0=Dom → 6
      return adjusted === i
    }).length
    return { day, hours: [Math.min(count, 3), 0, 0] }
  })
})

// ── Cargar datos ──────────────────────────────────────────────────
async function fetchData() {
  loading.value = true
  try {
    const [tasksRes, examRes] = await Promise.all([
      api.get(`/api/tasks/${authStore.userId}`),
      api.get(`/api/exams/${authStore.userId}/next`),
    ])
    tasks.value    = tasksRes.data
    nextExam.value = examRes.data   // null si no hay examen
  } catch (err) {
    console.error('Error cargando dashboard:', err)
  } finally {
    loading.value = false
  }
}

// ── Toggle tarea ──────────────────────────────────────────────────
async function toggleTask(task) {
  try {
    const { data } = await api.patch(`/api/tasks/${task.id}`, { done: !task.done })
    const idx = tasks.value.findIndex(t => t.id === task.id)
    if (idx !== -1) tasks.value[idx] = data
  } catch (err) {
    console.error('Error actualizando tarea:', err)
  }
}

// ── Eliminar tarea ────────────────────────────────────────────────
async function deleteTask(id) {
  try {
    await api.delete(`/api/tasks/${id}`)
    tasks.value = tasks.value.filter(t => t.id !== id)
  } catch (err) {
    console.error('Error eliminando tarea:', err)
  }
}

// ── Tarea creada desde el modal ───────────────────────────────────
function onTaskCreated(newTask) {
  tasks.value.unshift(newTask)
}

onMounted(fetchData)
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

h1 { font-size: 22px; font-weight: 600; color: var(--text-primary); }

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
  white-space: nowrap;
}

.loading-row {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
  font-size: 13px;
  padding: 2rem 0;
}

.spinner-lg {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-strong);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

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

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.filter-row {
  display: flex;
  gap: 4px;
}

.filter-btn {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 12px;
  border: 1px solid var(--border-strong);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}
.filter-btn.active {
  background: var(--accent-light);
  border-color: rgba(29,158,117,0.3);
  color: var(--accent-dark);
  font-weight: 500;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.empty-msg {
  font-size: 13px;
  color: var(--text-tertiary);
  text-align: center;
  padding: 1rem 0;
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
  font-family: 'DM Sans', sans-serif;
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
.ai-banner-text p { font-weight: 400; opacity: 0.85; margin: 0; }

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
