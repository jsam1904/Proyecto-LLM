<template>
  <div class="view">
    <header class="view-header">
      <div>
        <h1>Plan de estudio</h1>
        <p class="subtitle">Semana del {{ weekRange }} — generado por IA</p>
      </div>
      <button class="regen-btn" @click="regenerating = true" :disabled="regenerating">
        <span v-if="!regenerating">Regenerar con IA ↗</span>
        <span v-else>Generando...</span>
      </button>
    </header>

    <div class="plan-grid">
      <div v-for="day in plan" :key="day.name" class="day-card">
        <div class="day-head">
          <span class="day-name">{{ day.name }}</span>
          <span class="day-total">{{ totalHours(day) }}h planeadas</span>
        </div>
        <div v-if="day.slots.length" class="slots">
          <div v-for="slot in day.slots" :key="slot.time" class="slot">
            <span class="slot-time">{{ slot.time }}</span>
            <div class="slot-body">
              <span class="slot-subject">{{ slot.subject }}</span>
              <span :class="['slot-tag', tagClass(slot.tag)]">{{ slot.tag }}</span>
            </div>
            <span class="slot-dur">{{ slot.duration }} min</span>
          </div>
        </div>
        <div v-else class="no-slots">Sin bloques planeados</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const regenerating = ref(false)

const weekRange = new Date().toLocaleDateString('es-GT', { day: 'numeric', month: 'long' })

const plan = ref([
  {
    name: 'Lunes',
    slots: [
      { time: '7:00 – 8:30',   subject: 'Cálculo II — Integrales dobles',      tag: 'Cálculo', duration: 90 },
      { time: '10:00 – 11:30', subject: 'Programación — Proyecto Flask API',   tag: 'Prog',    duration: 90 },
      { time: '15:00 – 17:00', subject: 'Base de Datos — Normalización 3FN',   tag: 'BD',      duration: 120 },
    ]
  },
  {
    name: 'Martes',
    slots: [
      { time: '8:00 – 9:30',   subject: 'Inteligencia Artificial — Redes neuronales', tag: 'IA',      duration: 90 },
      { time: '14:00 – 15:30', subject: 'Cálculo II — Repaso para examen',            tag: 'Cálculo', duration: 90 },
    ]
  },
  {
    name: 'Miércoles',
    slots: [
      { time: '7:00 – 9:00',   subject: 'Cálculo II — Ejercicios tipo examen', tag: 'Cálculo', duration: 120 },
      { time: '11:00 – 12:00', subject: 'Programación — Testing unitario',      tag: 'Prog',    duration: 60 },
    ]
  },
  {
    name: 'Jueves',
    slots: [
      { time: '8:00 – 10:00', subject: 'Base de Datos — Consultas SQL avanzadas', tag: 'BD', duration: 120 },
      { time: '15:00 – 16:30', subject: 'IA — Implementación de modelo simple',   tag: 'IA', duration: 90 },
    ]
  },
  {
    name: 'Viernes',
    slots: [
      { time: '7:00 – 8:00', subject: 'Repaso general — Todas las materias', tag: 'Prog', duration: 60 },
    ]
  },
  { name: 'Sábado', slots: [] },
  { name: 'Domingo', slots: [] },
])

const tagMap = { 'Cálculo': 'tag-math', 'Prog': 'tag-prog', 'BD': 'tag-db', 'IA': 'tag-ia' }
function tagClass(tag) { return tagMap[tag] || 'tag-prog' }
function totalHours(day) {
  const mins = day.slots.reduce((s, sl) => s + sl.duration, 0)
  return (mins / 60).toFixed(1)
}
</script>

<style scoped>
.view { padding: 2rem; display: flex; flex-direction: column; gap: 1.25rem; }
.view-header { display: flex; justify-content: space-between; align-items: flex-start; }
h1 { font-size: 22px; font-weight: 600; }
.subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 3px; }

.regen-btn {
  font-size: 13px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(29,158,117,0.4);
  background: var(--accent-light);
  color: var(--accent-dark);
  cursor: pointer;
  font-weight: 500;
  transition: background 0.15s;
}
.regen-btn:hover { background: #c5eddf; }
.regen-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.plan-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.day-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  min-height: 200px;
}

.day-head {
  padding: 10px 12px;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border);
}

.day-name { font-size: 12px; font-weight: 600; color: var(--text-primary); display: block; }
.day-total { font-size: 10px; color: var(--text-tertiary); }

.slots { padding: 8px; display: flex; flex-direction: column; gap: 5px; }

.slot {
  padding: 7px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  font-size: 11px;
  background: var(--bg-page);
}

.slot-time { color: var(--text-tertiary); display: block; margin-bottom: 3px; }
.slot-body { display: flex; align-items: flex-start; justify-content: space-between; gap: 4px; }
.slot-subject { color: var(--text-primary); font-size: 11px; line-height: 1.4; flex: 1; }
.slot-dur { color: var(--text-tertiary); font-size: 10px; margin-top: 4px; display: block; }

.slot-tag {
  font-size: 9px;
  padding: 2px 5px;
  border-radius: 10px;
  white-space: nowrap;
  flex-shrink: 0;
}

.tag-math { background: var(--tag-math-bg); color: var(--tag-math-tx); }
.tag-prog { background: var(--tag-prog-bg); color: var(--tag-prog-tx); }
.tag-db   { background: var(--tag-db-bg);   color: var(--tag-db-tx); }
.tag-ia   { background: var(--tag-ia-bg);   color: var(--tag-ia-tx); }

.no-slots {
  padding: 16px 12px;
  font-size: 11px;
  color: var(--text-tertiary);
  text-align: center;
}
</style>
