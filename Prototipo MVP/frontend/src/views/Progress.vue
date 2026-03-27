<template>
  <div class="view">
    <header class="view-header">
      <h1>Progreso</h1>
      <p class="subtitle">Resumen del mes — seguimiento por materia</p>
    </header>

    <section class="metrics">
      <MetricCard label="Total horas mes" value="62" unit="h" trend="+8h vs mes anterior" />
      <MetricCard label="Materias activas" value="4" trend="Todas al día" />
      <MetricCard label="Objetivos cumplidos" value="73%" trend="11/15 completados" />
      <MetricCard label="Mejor materia" value="Programación" trend="82% de avance" />
    </section>

    <div class="two-col">
      <div class="card">
        <h2 class="card-title">Avance por materia</h2>
        <div class="progress-list">
          <ProgressRow v-for="s in subjects" :key="s.name" :subject="s" />
        </div>
      </div>

      <div class="card">
        <h2 class="card-title">Distribución de horas</h2>
        <div class="donut-wrap">
          <svg viewBox="0 0 120 120" class="donut">
            <circle cx="60" cy="60" r="48" fill="none" stroke="#F0EEE8" stroke-width="16"/>
            <circle cx="60" cy="60" r="48" fill="none" stroke="#378ADD" stroke-width="16"
              stroke-dasharray="75.4 225.2" stroke-dashoffset="0" stroke-linecap="round"/>
            <circle cx="60" cy="60" r="48" fill="none" stroke="#1D9E75" stroke-width="16"
              stroke-dasharray="51.4 249.1" stroke-dashoffset="-75.4" stroke-linecap="round"/>
            <circle cx="60" cy="60" r="48" fill="none" stroke="#BA7517" stroke-width="16"
              stroke-dasharray="42.5 257.9" stroke-dashoffset="-126.8" stroke-linecap="round"/>
            <circle cx="60" cy="60" r="48" fill="none" stroke="#7F77DD" stroke-width="16"
              stroke-dasharray="31.4 268.9" stroke-dashoffset="-169.3" stroke-linecap="round"/>
            <text x="60" y="55" text-anchor="middle" font-size="14" font-weight="600" fill="#1A1A18">62h</text>
            <text x="60" y="70" text-anchor="middle" font-size="8" fill="#A3A39E">este mes</text>
          </svg>
          <div class="legend">
            <div v-for="s in subjects" :key="s.name" class="legend-item">
              <span class="legend-dot" :style="{ background: s.color }"></span>
              <span>{{ s.name }}</span>
              <span class="legend-val">{{ s.hours }}h</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import MetricCard from '../components/MetricCard.vue'
import ProgressRow from '../components/ProgressRow.vue'

const subjects = [
  { name: 'Cálculo II',             pct: 55, hours: 18, color: '#378ADD' },
  { name: 'Programación',           pct: 82, hours: 22, color: '#1D9E75' },
  { name: 'Base de Datos',          pct: 68, hours: 14, color: '#BA7517' },
  { name: 'Inteligencia Artificial',pct: 40, hours: 8,  color: '#7F77DD' },
]
</script>

<style scoped>
.view { padding: 2rem; display: flex; flex-direction: column; gap: 1.25rem; }
.view-header h1 { font-size: 22px; font-weight: 600; }
.subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 3px; }
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 10px; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.25rem; }
.card-title { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 16px; }
.progress-list { display: flex; flex-direction: column; gap: 14px; }
.donut-wrap { display: flex; align-items: center; gap: 1.5rem; }
.donut { width: 120px; flex-shrink: 0; }
.legend { display: flex; flex-direction: column; gap: 10px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-secondary); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-val { margin-left: auto; font-weight: 500; color: var(--text-primary); }
</style>
