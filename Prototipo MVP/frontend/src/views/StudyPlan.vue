<template>
  <div class="view">
    <header class="view-header">
      <div>
        <h1>Plan de estudio</h1>
        <p class="subtitle" v-if="plan">
          Semana del {{ weekRange }} —
          <span v-if="editMode" style="color: var(--accent-dark); font-weight: 500;">modo edición</span>
          <span v-else>generado por IA</span>
        </p>
        <p class="subtitle" v-else>Genera tu plan semanal personalizado con IA</p>
      </div>
      <div class="header-actions">
        <template v-if="editMode">
          <button class="cancel-btn" @click="cancelEdit">Cancelar</button>
          <button class="save-btn" @click="saveEdit" :disabled="saving">
            <span v-if="saving" class="spinner"></span>
            <span v-else>Guardar cambios</span>
          </button>
        </template>
        <template v-else>
          <button v-if="plan" class="edit-btn" @click="enterEdit">Editar</button>
          <button class="regen-btn" @click="showForm = true">
            {{ plan ? 'Regenerar ↗' : 'Generar plan ↗' }}
          </button>
        </template>
      </div>
    </header>

    <!-- Cargando -->
    <div v-if="loading" class="loading-row">
      <span class="spinner-lg"></span> Cargando plan...
    </div>

    <!-- Sin plan aún -->
    <div v-else-if="!plan" class="empty-plan">
      <div class="empty-icon">📅</div>
      <h3>No tienes un plan generado aún</h3>
      <p>Haz clic en "Generar plan" para que la IA cree tu horario semanal personalizado.</p>
      <button class="regen-btn" @click="showForm = true">Generar mi primer plan ↗</button>
    </div>

    <!-- Plan generado -->
    <div v-else class="plan-grid">
      <div v-for="(day, dayIdx) in displayPlan.days" :key="day.name" class="day-card">
        <div class="day-head">
          <span class="day-name">{{ day.name }}</span>
          <span v-if="!editMode" class="day-total">{{ totalHours(day) }}h</span>
          <button v-else class="add-slot-btn" @click="addSlot(dayIdx)" title="Agregar sesión">+</button>
        </div>

        <div v-if="day.slots.length" class="slots">
          <!-- Vista normal -->
          <template v-if="!editMode">
            <div v-for="slot in day.slots" :key="slot.time" class="slot">
              <span class="slot-time">{{ slot.time }}</span>
              <div class="slot-body">
                <span class="slot-subject">{{ slot.subject }}</span>
                <span :class="['slot-tag', tagClass(slot.tag)]">{{ slot.tag }}</span>
              </div>
              <span class="slot-dur">{{ slot.duration }} min</span>
            </div>
          </template>

          <!-- Modo edición -->
          <template v-else>
            <div v-for="(slot, slotIdx) in day.slots" :key="slotIdx" class="slot editing">
              <div class="edit-time-row">
                <input
                  type="time"
                  :value="getStart(slot.time)"
                  @change="onTimeChange(slot, 'start', $event)"
                  class="edit-input edit-time-pick"
                />
                <span class="time-sep">–</span>
                <input
                  type="time"
                  :value="getEnd(slot.time)"
                  @change="onTimeChange(slot, 'end', $event)"
                  class="edit-input edit-time-pick"
                />
                <button class="del-slot-btn" @click="removeSlot(dayIdx, slotIdx)" title="Eliminar">✕</button>
              </div>
              <input
                v-model="slot.subject"
                class="edit-input edit-subject"
                placeholder="Materia o actividad"
              />
              <div class="edit-row-bottom">
                <input v-model="slot.tag" class="edit-input edit-tag" placeholder="Tag" />
                <span class="edit-dur-display">{{ slot.duration }} min</span>
              </div>
            </div>
          </template>
        </div>

        <div v-else class="no-slots">
          {{ editMode ? '— sin sesiones —' : 'Día libre' }}
        </div>

        <button v-if="editMode" class="add-slot-full-btn" @click="addSlot(dayIdx)">
          + Agregar sesión
        </button>
      </div>
    </div>

    <!-- Error al guardar -->
    <p v-if="saveError" class="error-msg-bar">{{ saveError }}</p>

    <!-- Panel lateral: Formulario para generar plan -->
    <Teleport to="body">
      <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
        <div class="form-panel">
          <div class="form-header">
            <h3>Configurar plan semanal</h3>
            <button class="close-btn" @click="showForm = false">✕</button>
          </div>

          <div class="form-body">
            <!-- Semana -->
            <div class="field">
              <label>Inicio de la semana</label>
              <input v-model="form.week_start" type="date" />
            </div>

            <!-- Materias -->
            <div class="field">
              <label>Materias <span class="required">*</span></label>
              <div class="tag-input-row">
                <input
                  v-model="subjectInput"
                  type="text"
                  placeholder="Ej: Cálculo II"
                  @keydown.enter.prevent="addSubject"
                />
                <button type="button" class="add-tag-btn" @click="addSubject">+</button>
              </div>
              <div class="tag-list">
                <span v-for="s in form.subjects" :key="s" class="subject-tag">
                  {{ s }}
                  <button @click="removeSubject(s)">✕</button>
                </span>
              </div>
            </div>

            <!-- Horas disponibles por día -->
            <div class="field">
              <label>Horas disponibles por día</label>
              <div class="hours-grid">
                <div v-for="(day, key) in form.available_hours" :key="key" class="hour-row">
                  <span class="day-label">{{ dayLabels[key] }}</span>
                  <input
                    v-model.number="form.available_hours[key]"
                    type="number"
                    min="0"
                    max="12"
                    step="0.5"
                    class="hour-input"
                  />
                  <span class="hour-unit">h</span>
                </div>
              </div>
            </div>

            <!-- Materias prioritarias -->
            <div class="field" v-if="form.subjects.length">
              <label>Materias prioritarias</label>
              <div class="tag-row">
                <button
                  v-for="s in form.subjects"
                  :key="s"
                  type="button"
                  :class="['tag-btn', { active: form.priorities.includes(s) }]"
                  @click="togglePriority(s)"
                >
                  {{ s }}
                </button>
              </div>
            </div>

            <!-- Botón generar -->
            <button
              class="generate-btn"
              @click="generatePlan"
              :disabled="generating || !form.subjects.length"
            >
              <span v-if="generating" class="spinner"></span>
              <span v-else>🤖 Generar plan con IA</span>
            </button>

            <p v-if="generateError" class="error-msg">{{ generateError }}</p>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import api from '../services/api.js'
import { useAuthStore } from '../stores/auth.js'

const authStore = useAuthStore()
const loading        = ref(true)
const plan           = ref(null)
const planId         = ref(null)
const editMode       = ref(false)
const editingPlan    = ref(null)
const saving         = ref(false)
const saveError      = ref('')
const showForm       = ref(false)
const generating     = ref(false)
const generateError  = ref('')
const subjectInput   = ref('')

function nextMonday() {
  const d = new Date()
  const day = d.getDay()
  const diff = day === 0 ? 1 : (8 - day) % 7 || 7
  d.setDate(d.getDate() + (day === 1 ? 0 : diff))
  return d.toISOString().split('T')[0]
}

const form = reactive({
  week_start: nextMonday(),
  subjects: [],
  priorities: [],
  available_hours: {
    monday: 4, tuesday: 3, wednesday: 4,
    thursday: 3, friday: 2, saturday: 1, sunday: 0,
  },
})

const dayLabels = {
  monday: 'Lunes', tuesday: 'Martes', wednesday: 'Miércoles',
  thursday: 'Jueves', friday: 'Viernes', saturday: 'Sábado', sunday: 'Domingo',
}

const displayPlan = computed(() => editMode.value ? editingPlan.value : plan.value)

const weekRange = computed(() => {
  const src = plan.value?.week_start
  if (!src) return ''
  return new Date(src + 'T12:00:00')
    .toLocaleDateString('es-GT', { day: 'numeric', month: 'long', year: 'numeric' })
})

const tagMap = { 'Cálculo': 'tag-math', 'Prog': 'tag-prog', 'BD': 'tag-db', 'IA': 'tag-ia' }
function tagClass(tag) { return tagMap[tag] || 'tag-prog' }
function totalHours(day) {
  const mins = day.slots.reduce((s, sl) => s + (sl.duration || 0), 0)
  return (mins / 60).toFixed(1)
}

// ── Materias ──────────────────────────────────────────────────────
function addSubject() {
  const s = subjectInput.value.trim()
  if (s && !form.subjects.includes(s)) form.subjects.push(s)
  subjectInput.value = ''
}
function removeSubject(s) {
  form.subjects = form.subjects.filter(x => x !== s)
  form.priorities = form.priorities.filter(x => x !== s)
}
function togglePriority(s) {
  const idx = form.priorities.indexOf(s)
  if (idx === -1) form.priorities.push(s)
  else form.priorities.splice(idx, 1)
}

// ── Helpers de tiempo ────────────────────────────────────────────
function getStart(timeStr) {
  return timeStr?.split(/\s*[–—\-]\s*/)[0]?.trim() || ''
}
function getEnd(timeStr) {
  const parts = timeStr?.split(/\s*[–—\-]\s*/)
  return parts?.length > 1 ? parts[1].trim() : ''
}
function onTimeChange(slot, type, event) {
  const val   = event.target.value
  const start = type === 'start' ? val : getStart(slot.time)
  const end   = type === 'end'   ? val : getEnd(slot.time)
  slot.time = start && end ? `${start} – ${end}` : (start || end || '')
  if (start && end) {
    const [sh, sm] = start.split(':').map(Number)
    const [eh, em] = end.split(':').map(Number)
    const diff = (eh * 60 + em) - (sh * 60 + sm)
    if (diff > 0) slot.duration = diff
  }
}

// ── Edición manual ────────────────────────────────────────────────
function enterEdit() {
  editingPlan.value = JSON.parse(JSON.stringify(plan.value))
  saveError.value = ''
  editMode.value = true
}

function cancelEdit() {
  editMode.value = false
  editingPlan.value = null
  saveError.value = ''
}

function addSlot(dayIdx) {
  editingPlan.value.days[dayIdx].slots.push({
    time: '',
    subject: '',
    tag: 'Estudio',
    duration: 60,
  })
}

function removeSlot(dayIdx, slotIdx) {
  editingPlan.value.days[dayIdx].slots.splice(slotIdx, 1)
}

async function saveEdit() {
  saving.value = true
  saveError.value = ''
  try {
    const { data } = await api.put(`/api/plan/${planId.value}`, {
      plan_data: editingPlan.value,
    })
    plan.value = data.plan
    editMode.value = false
    editingPlan.value = null
  } catch (err) {
    saveError.value = err.response?.data?.detail || 'Error al guardar. Intenta de nuevo.'
  } finally {
    saving.value = false
  }
}

// ── Cargar plan existente ─────────────────────────────────────────
async function fetchPlan() {
  loading.value = true
  try {
    const { data } = await api.get(`/api/plan/${authStore.userId}/latest`)
    plan.value = data.plan
    planId.value = data.plan_id
  } catch (err) {
    if (err.response?.status !== 404) console.error('Error cargando plan:', err)
    plan.value = null
  } finally {
    loading.value = false
  }
}

// ── Generar plan con IA ───────────────────────────────────────────
async function generatePlan() {
  if (!form.subjects.length) return
  generating.value   = true
  generateError.value = ''
  try {
    const { data } = await api.post('/api/plan/generate', {
      user_id:         authStore.userId,
      week_start:      form.week_start,
      subjects:        form.subjects,
      available_hours: form.available_hours,
      priorities:      form.priorities.length ? form.priorities : null,
    })
    plan.value = data.plan
    planId.value = data.plan_id
    showForm.value = false
  } catch (err) {
    generateError.value =
      err.response?.data?.detail || 'Error al generar el plan. Intenta de nuevo.'
  } finally {
    generating.value = false
  }
}

onMounted(fetchPlan)
</script>

<style scoped>
.view { padding: 2rem; display: flex; flex-direction: column; gap: 1.25rem; }
.view-header { display: flex; justify-content: space-between; align-items: flex-start; }
h1 { font-size: 22px; font-weight: 600; }
.subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 3px; }

.header-actions { display: flex; gap: 8px; align-items: center; }

.regen-btn {
  font-size: 13px; padding: 8px 16px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(29,158,117,0.4);
  background: var(--accent-light); color: var(--accent-dark);
  cursor: pointer; font-weight: 500;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.15s; white-space: nowrap;
}
.regen-btn:hover { background: #c5eddf; }

.edit-btn {
  font-size: 13px; padding: 8px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-strong);
  background: transparent; color: var(--text-secondary);
  cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}
.edit-btn:hover { background: var(--bg-hover); color: var(--text-primary); }

.save-btn {
  font-size: 13px; padding: 8px 16px;
  border-radius: var(--radius-md);
  border: none;
  background: var(--accent); color: white;
  cursor: pointer; font-weight: 500;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.15s;
  display: flex; align-items: center; gap: 6px;
}
.save-btn:hover:not(:disabled) { background: var(--accent-dark); }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.cancel-btn {
  font-size: 13px; padding: 8px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-strong);
  background: transparent; color: var(--text-secondary);
  cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}
.cancel-btn:hover { background: var(--bg-hover); }

.error-msg-bar {
  font-size: 12px; color: #b91c1c;
  background: #fee2e2; border-radius: var(--radius-sm);
  padding: 8px 12px; margin: 0;
}

.loading-row {
  display: flex; align-items: center; gap: 10px;
  color: var(--text-secondary); font-size: 13px; padding: 2rem 0;
}
.spinner-lg {
  width: 20px; height: 20px;
  border: 2px solid var(--border-strong); border-top-color: var(--accent);
  border-radius: 50%; animation: spin 0.7s linear infinite; display: inline-block;
}

.empty-plan {
  display: flex; flex-direction: column; align-items: center;
  gap: 10px; padding: 4rem 2rem; text-align: center; color: var(--text-secondary);
}
.empty-icon { font-size: 3rem; }
.empty-plan h3 { font-size: 16px; color: var(--text-primary); margin: 0; }
.empty-plan p { font-size: 13px; margin: 0; max-width: 360px; }

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
  display: flex; flex-direction: column;
}

.day-head {
  padding: 8px 10px;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.day-name  { font-size: 12px; font-weight: 600; color: var(--text-primary); }
.day-total { font-size: 10px; color: var(--text-tertiary); }

.add-slot-btn {
  width: 20px; height: 20px; border-radius: 50%;
  border: 1px solid var(--accent); background: var(--accent-light);
  color: var(--accent-dark); font-size: 14px; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-family: 'DM Sans', sans-serif; transition: all 0.15s; flex-shrink: 0;
}
.add-slot-btn:hover { background: var(--accent); color: white; }

.slots { padding: 6px; display: flex; flex-direction: column; gap: 5px; flex: 1; }

/* Slot vista normal */
.slot {
  padding: 7px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  font-size: 11px;
  background: var(--bg-page);
}
.slot-time    { color: var(--text-tertiary); display: block; margin-bottom: 3px; }
.slot-body    { display: flex; align-items: flex-start; justify-content: space-between; gap: 4px; }
.slot-subject { color: var(--text-primary); font-size: 11px; line-height: 1.4; flex: 1; }
.slot-dur     { color: var(--text-tertiary); font-size: 10px; margin-top: 4px; display: block; }

/* Slot edición */
.slot.editing {
  border-color: rgba(29,158,117,0.3);
  background: var(--bg-page);
  display: flex; flex-direction: column; gap: 4px;
}
.edit-time-row {
  display: flex; gap: 3px; align-items: center;
}
.edit-row-bottom {
  display: flex; gap: 4px; align-items: center;
}
.time-sep {
  font-size: 10px; color: var(--text-tertiary); flex-shrink: 0;
}
.edit-input {
  font-size: 11px; font-family: 'DM Sans', sans-serif;
  padding: 3px 6px;
  border: 1px solid var(--border-strong);
  border-radius: 4px;
  background: var(--bg-surface);
  color: var(--text-primary);
  outline: none; transition: border-color 0.15s;
}
.edit-input:focus { border-color: var(--accent); }
.edit-time-pick {
  flex: 1; min-width: 0;
  padding: 3px 4px;
  font-size: 10px;
}
.edit-time-pick::-webkit-calendar-picker-indicator {
  width: 10px; opacity: 0.5; cursor: pointer;
}
.edit-subject { width: 100%; }
.edit-tag     { flex: 1; min-width: 0; }
.edit-dur-display {
  font-size: 10px; color: var(--text-tertiary);
  white-space: nowrap; padding: 0 2px;
  background: var(--bg-hover); border-radius: 4px; padding: 2px 5px;
}

.del-slot-btn {
  width: 18px; height: 18px; border-radius: 50%;
  border: 1px solid #fca5a5; background: #fee2e2;
  color: #b91c1c; font-size: 9px; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.15s;
}
.del-slot-btn:hover { background: #b91c1c; color: white; border-color: #b91c1c; }

.slot-tag {
  font-size: 9px; padding: 2px 5px;
  border-radius: 10px; white-space: nowrap; flex-shrink: 0;
}
.tag-math { background: var(--tag-math-bg); color: var(--tag-math-tx); }
.tag-prog { background: var(--tag-prog-bg); color: var(--tag-prog-tx); }
.tag-db   { background: var(--tag-db-bg);   color: var(--tag-db-tx); }
.tag-ia   { background: var(--tag-ia-bg);   color: var(--tag-ia-tx); }

.no-slots {
  padding: 16px 12px; font-size: 11px;
  color: var(--text-tertiary); text-align: center; flex: 1;
  display: flex; align-items: center; justify-content: center;
}

.add-slot-full-btn {
  width: 100%; padding: 6px;
  font-size: 11px; color: var(--accent-dark);
  background: var(--accent-light);
  border: none; border-top: 1px solid rgba(29,158,117,0.2);
  cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: background 0.15s;
}
.add-slot-full-btn:hover { background: #c5eddf; }

/* ── Modal Formulario ── */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; backdrop-filter: blur(2px);
}
.form-panel {
  background: var(--bg-surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  width: 100%; max-width: 500px;
  max-height: 85vh; overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  animation: slide-up 0.18s ease;
}
@keyframes slide-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes spin { to { transform: rotate(360deg); } }

.form-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 1.25rem 0;
}
.form-header h3 { font-size: 15px; font-weight: 600; color: var(--text-primary); margin: 0; }
.close-btn {
  background: none; border: none; font-size: 14px;
  color: var(--text-tertiary); cursor: pointer;
  padding: 4px 6px; border-radius: 4px; transition: background 0.15s;
}
.close-btn:hover { background: var(--bg-hover); }

.form-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12px; font-weight: 500; color: var(--text-secondary); }
.required { color: #e53e3e; }

.field input[type="date"],
.field input[type="text"] {
  padding: 9px 12px;
  border: 1px solid var(--border-strong); border-radius: var(--radius-md);
  background: var(--bg-page); color: var(--text-primary);
  font-size: 13px; font-family: 'DM Sans', sans-serif;
  outline: none; transition: border-color 0.15s;
}
.field input:focus { border-color: var(--accent); }

.tag-input-row { display: flex; gap: 6px; }
.tag-input-row input { flex: 1; }
.add-tag-btn {
  padding: 9px 14px; border-radius: var(--radius-md);
  border: 1px solid var(--border-strong); background: transparent;
  color: var(--text-secondary); font-size: 16px; cursor: pointer;
  font-family: 'DM Sans', sans-serif; transition: all 0.15s;
}
.add-tag-btn:hover { background: var(--accent-light); color: var(--accent-dark); }

.tag-list { display: flex; flex-wrap: wrap; gap: 6px; }
.subject-tag {
  display: flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 20px;
  background: var(--accent-light); color: var(--accent-dark);
  font-size: 12px; font-weight: 500;
}
.subject-tag button {
  background: none; border: none; color: inherit;
  cursor: pointer; padding: 0; font-size: 10px; line-height: 1;
}

.hours-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.hour-row { display: flex; align-items: center; gap: 8px; }
.day-label { font-size: 12px; color: var(--text-secondary); width: 70px; }
.hour-input {
  width: 56px; padding: 6px 8px;
  border: 1px solid var(--border-strong); border-radius: var(--radius-sm);
  background: var(--bg-page); color: var(--text-primary);
  font-size: 13px; font-family: 'DM Sans', sans-serif;
  outline: none; text-align: center;
}
.hour-input:focus { border-color: var(--accent); }
.hour-unit { font-size: 12px; color: var(--text-tertiary); }

.tag-row { display: flex; flex-wrap: wrap; gap: 6px; }
.tag-btn {
  padding: 4px 12px; border-radius: 20px;
  border: 1px solid var(--border-strong);
  background: transparent; color: var(--text-secondary);
  font-size: 12px; cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}
.tag-btn.active {
  background: var(--accent-light); border-color: rgba(29,158,117,0.4);
  color: var(--accent-dark); font-weight: 500;
}

.generate-btn {
  padding: 11px; background: var(--accent); color: white;
  border: none; border-radius: var(--radius-md);
  font-size: 14px; font-weight: 600;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer; transition: background 0.15s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.generate-btn:hover { background: var(--accent-dark); }
.generate-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.error-msg {
  font-size: 12px; color: #b91c1c;
  background: #fee2e2; border-radius: var(--radius-sm);
  padding: 8px 12px; margin: 0;
}
</style>
