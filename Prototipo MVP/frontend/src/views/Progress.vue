<template>
  <div class="view">
    <header class="view-header">
      <h1>Progreso</h1>
      <p class="subtitle">Seguimiento real de tus tareas y horas de estudio</p>
    </header>

    <!-- Cargando -->
    <div v-if="loading" class="loading-row">
      <span class="spinner-lg"></span> Cargando estadísticas...
    </div>

    <template v-else>
      <!-- Métricas principales -->
      <section class="metrics">
        <MetricCard
          label="Tareas completadas"
          :value="`${stats.tasks.done}/${stats.tasks.total}`"
          :trend="`${stats.tasks.completion_pct}% completado`"
        />
        <MetricCard
          label="Tareas pendientes"
          :value="stats.tasks.pending"
          unit=" pendientes"
          trend="Por completar"
        />
        <MetricCard
          label="Horas planeadas"
          :value="stats.study_hours.total"
          unit="h"
          trend="Plan de estudio actual"
        />
        <MetricCard
          v-if="stats.next_exam"
          label="Próximo examen"
          :value="`${stats.next_exam.days_remaining} días`"
          :trend="stats.next_exam.subject"
        />
        <MetricCard
          v-else
          label="Exámenes"
          value="—"
          trend="Sin exámenes registrados"
        />
      </section>

      <div class="two-col">
        <!-- Avance por materia (tareas) -->
        <div class="card">
          <h2 class="card-title">Tareas por materia</h2>
          <div v-if="Object.keys(stats.tasks.by_subject).length" class="progress-list">
            <div
              v-for="(data, subject) in stats.tasks.by_subject"
              :key="subject"
              class="progress-row-item"
            >
              <div class="progress-meta">
                <span class="progress-name">{{ subject }}</span>
                <span class="progress-pct">
                  {{ data.total > 0 ? Math.round(data.done / data.total * 100) : 0 }}%
                </span>
              </div>
              <div class="progress-track">
                <div
                  class="progress-fill"
                  :style="{
                    width: data.total > 0 ? (data.done / data.total * 100) + '%' : '0%'
                  }"
                ></div>
              </div>
              <span class="progress-count">{{ data.done }}/{{ data.total }}</span>
            </div>
          </div>
          <p v-else class="empty-msg">No hay tareas registradas aún.</p>
        </div>

        <!-- Distribución de horas (planes) -->
        <div class="card">
          <h2 class="card-title">Distribución de horas planeadas</h2>
          <div v-if="Object.keys(stats.study_hours.by_subject).length" class="donut-wrap">
            <svg viewBox="0 0 120 120" class="donut">
              <circle cx="60" cy="60" r="48" fill="none" stroke="#F0EEE8" stroke-width="16"/>
              <circle
                v-for="(seg, i) in donutSegments"
                :key="i"
                cx="60" cy="60" r="48"
                fill="none"
                :stroke="seg.color"
                stroke-width="16"
                :stroke-dasharray="`${seg.dash} ${seg.gap}`"
                :stroke-dashoffset="-seg.offset"
                stroke-linecap="round"
              />
              <text x="60" y="55" text-anchor="middle" font-size="14" font-weight="600" fill="#1A1A18">
                {{ stats.study_hours.total }}h
              </text>
              <text x="60" y="70" text-anchor="middle" font-size="8" fill="#A3A39E">planeadas</text>
            </svg>
            <div class="legend">
              <div v-for="(seg, i) in donutSegments" :key="i" class="legend-item">
                <span class="legend-dot" :style="{ background: seg.color }"></span>
                <span>{{ seg.label }}</span>
                <span class="legend-val">{{ seg.hours }}h</span>
              </div>
            </div>
          </div>
          <p v-else class="empty-msg">
            Genera un plan de estudio para ver la distribución de horas.
          </p>
        </div>
      </div>

      <!-- Agregar examen -->
      <div class="card exam-card">
        <div class="exam-header">
          <h2 class="card-title">Exámenes próximos</h2>
          <button class="add-exam-btn" @click="showExamForm = !showExamForm">
            {{ showExamForm ? 'Cancelar' : '+ Agregar examen' }}
          </button>
        </div>

        <!-- Formulario agregar examen -->
        <form v-if="showExamForm" @submit.prevent="addExam" class="exam-form">
          <input v-model="examForm.subject"   type="text"     placeholder="Materia"   required />
          <input v-model="examForm.exam_date" type="datetime-local" required />
          <input v-model="examForm.notes"     type="text"     placeholder="Notas (opcional)" />
          <button type="submit" class="exam-save-btn" :disabled="savingExam">
            <span v-if="savingExam" class="spinner-sm"></span>
            <span v-else>Guardar</span>
          </button>
        </form>

        <!-- Lista de exámenes -->
        <div v-if="exams.length" class="exam-list">
          <div v-for="exam in exams" :key="exam.id" class="exam-item">
            <div class="exam-info">
              <span class="exam-subject">{{ exam.subject }}</span>
              <span class="exam-date">{{ formatDate(exam.exam_date) }}</span>
              <span v-if="exam.notes" class="exam-notes">{{ exam.notes }}</span>
            </div>
            <span :class="['days-badge', daysClass(exam)]">
              {{ daysUntil(exam.exam_date) }}
            </span>
            <button class="del-btn" @click="deleteExam(exam.id)">✕</button>
          </div>
        </div>
        <p v-else-if="!showExamForm" class="empty-msg">No tienes exámenes registrados.</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import MetricCard from '../components/MetricCard.vue'
import api from '../services/api.js'
import { useAuthStore } from '../stores/auth.js'

const authStore = useAuthStore()
const loading   = ref(true)
const exams     = ref([])
const showExamForm = ref(false)
const savingExam   = ref(false)

const examForm = reactive({ subject: '', exam_date: '', notes: '' })

const stats = ref({
  tasks:       { total: 0, done: 0, pending: 0, completion_pct: 0, by_subject: {} },
  study_hours: { total: 0, by_subject: {} },
  next_exam:   null,
})

// Colores para el donut
const COLORS = ['#378ADD', '#1D9E75', '#BA7517', '#7F77DD', '#E05252', '#45B7D1']
const circumference = 2 * Math.PI * 48  // ≈ 301.6

const donutSegments = computed(() => {
  const entries = Object.entries(stats.value.study_hours.by_subject)
  if (!entries.length) return []
  const total = stats.value.study_hours.total || 1
  let offset = 0
  return entries.map(([label, hours], i) => {
    const fraction = hours / total
    const dash = fraction * circumference
    const seg  = { label, hours, color: COLORS[i % COLORS.length], dash, gap: circumference - dash, offset }
    offset += dash
    return seg
  })
})

// ── Cargar datos ──────────────────────────────────────────────────
async function fetchData() {
  loading.value = true
  try {
    const [progressRes, examsRes] = await Promise.all([
      api.get(`/api/progress/${authStore.userId}`),
      api.get(`/api/exams/${authStore.userId}`),
    ])
    stats.value = progressRes.data
    exams.value = examsRes.data
  } catch (err) {
    console.error('Error cargando progreso:', err)
  } finally {
    loading.value = false
  }
}

// ── Helpers de fecha ──────────────────────────────────────────────
function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('es-GT', {
    weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

function daysUntil(dateStr) {
  const d = Math.ceil((new Date(dateStr) - new Date()) / (1000 * 60 * 60 * 24))
  if (d < 0)  return 'Pasado'
  if (d === 0) return 'Hoy'
  if (d === 1) return 'Mañana'
  return `${d} días`
}

function daysClass(exam) {
  const d = Math.ceil((new Date(exam.exam_date) - new Date()) / (1000 * 60 * 60 * 24))
  if (d < 0)  return 'badge-gray'
  if (d <= 3) return 'badge-red'
  if (d <= 7) return 'badge-yellow'
  return 'badge-green'
}

// ── Exámenes ──────────────────────────────────────────────────────
async function addExam() {
  savingExam.value = true
  try {
    const { data } = await api.post('/api/exams/', {
      user_id:   authStore.userId,
      subject:   examForm.subject,
      exam_date: new Date(examForm.exam_date).toISOString(),
      notes:     examForm.notes || null,
    })
    exams.value.push(data)
    exams.value.sort((a, b) => new Date(a.exam_date) - new Date(b.exam_date))
    showExamForm.value = false
    examForm.subject = examForm.exam_date = examForm.notes = ''
    // Recargar stats (actualiza next_exam)
    const res = await api.get(`/api/progress/${authStore.userId}`)
    stats.value = res.data
  } catch (err) {
    console.error('Error guardando examen:', err)
  } finally {
    savingExam.value = false
  }
}

async function deleteExam(id) {
  try {
    await api.delete(`/api/exams/${id}`)
    exams.value = exams.value.filter(e => e.id !== id)
    const res = await api.get(`/api/progress/${authStore.userId}`)
    stats.value = res.data
  } catch (err) {
    console.error('Error eliminando examen:', err)
  }
}

onMounted(fetchData)
</script>

<style scoped>
.view { padding: 2rem; display: flex; flex-direction: column; gap: 1.25rem; }
.view-header h1 { font-size: 22px; font-weight: 600; }
.subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 3px; }

.loading-row {
  display: flex; align-items: center; gap: 10px;
  color: var(--text-secondary); font-size: 13px; padding: 2rem 0;
}
.spinner-lg {
  width: 20px; height: 20px;
  border: 2px solid var(--border-strong);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
.spinner-sm {
  width: 13px; height: 13px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

.metrics { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 10px; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
}
.card-title { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 16px; }

.progress-list { display: flex; flex-direction: column; gap: 12px; }

.progress-row-item { display: flex; flex-direction: column; gap: 4px; }
.progress-meta { display: flex; justify-content: space-between; }
.progress-name { font-size: 12px; color: var(--text-primary); }
.progress-pct  { font-size: 12px; font-weight: 600; color: var(--accent-dark); }

.progress-track {
  height: 6px; background: var(--bg-hover);
  border-radius: 10px; overflow: hidden;
}
.progress-fill {
  height: 100%; background: var(--accent);
  border-radius: 10px; transition: width 0.5s ease;
}
.progress-count { font-size: 10px; color: var(--text-tertiary); }

.empty-msg {
  font-size: 13px; color: var(--text-tertiary);
  text-align: center; padding: 1.5rem 0;
}

/* Donut */
.donut-wrap { display: flex; align-items: center; gap: 1.5rem; }
.donut { width: 120px; flex-shrink: 0; }
.legend { display: flex; flex-direction: column; gap: 10px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-secondary); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-val { margin-left: auto; font-weight: 500; color: var(--text-primary); }

/* Exámenes */
.exam-card {}
.exam-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.exam-header .card-title { margin-bottom: 0; }

.add-exam-btn {
  font-size: 12px; padding: 6px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-strong);
  background: transparent; color: var(--text-secondary);
  cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}
.add-exam-btn:hover { background: var(--accent-light); color: var(--accent-dark); }

.exam-form {
  display: flex; flex-wrap: wrap; gap: 8px;
  padding: 12px; background: var(--bg-hover);
  border-radius: var(--radius-md); margin-bottom: 12px;
}
.exam-form input {
  flex: 1; min-width: 140px;
  padding: 8px 10px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  background: var(--bg-page); color: var(--text-primary);
  font-size: 13px; font-family: 'DM Sans', sans-serif; outline: none;
}
.exam-form input:focus { border-color: var(--accent); }
.exam-save-btn {
  padding: 8px 16px;
  background: var(--accent); color: white;
  border: none; border-radius: var(--radius-sm);
  font-size: 13px; font-weight: 600;
  font-family: 'DM Sans', sans-serif; cursor: pointer;
  display: flex; align-items: center; gap: 6px;
  transition: background 0.15s;
}
.exam-save-btn:hover { background: var(--accent-dark); }

.exam-list { display: flex; flex-direction: column; gap: 6px; }
.exam-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-page);
}
.exam-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.exam-subject { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.exam-date    { font-size: 11px; color: var(--text-secondary); }
.exam-notes   { font-size: 11px; color: var(--text-tertiary); }

.days-badge {
  font-size: 11px; font-weight: 600;
  padding: 3px 10px; border-radius: 12px; white-space: nowrap; flex-shrink: 0;
}
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-yellow { background: #fef9c3; color: #854d0e; }
.badge-green  { background: var(--accent-light); color: var(--accent-dark); }
.badge-gray   { background: var(--bg-hover); color: var(--text-tertiary); }

.del-btn {
  background: none; border: none; color: var(--text-tertiary);
  cursor: pointer; font-size: 12px; padding: 4px 6px;
  border-radius: 4px; transition: all 0.15s; flex-shrink: 0;
}
.del-btn:hover { background: #fee2e2; color: #b91c1c; }
</style>
