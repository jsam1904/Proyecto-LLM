<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal">
        <div class="modal-header">
          <h3>Nueva tarea</h3>
          <button class="close-btn" @click="$emit('close')">✕</button>
        </div>

        <form @submit.prevent="submit" class="modal-body">
          <!-- Texto de la tarea -->
          <div class="field">
            <label>Tarea <span class="required">*</span></label>
            <input
              v-model="form.text"
              type="text"
              placeholder="Ej: Resolver ejercicios de integrales"
              required
              autofocus
            />
          </div>

          <!-- Materia -->
          <div class="field">
            <label>Materia</label>
            <input
              v-model="form.subject"
              type="text"
              placeholder="Ej: Cálculo II"
              list="subject-suggestions"
            />
            <datalist id="subject-suggestions">
              <option v-for="s in subjectSuggestions" :key="s" :value="s" />
            </datalist>
          </div>

          <!-- Etiqueta -->
          <div class="field">
            <label>Etiqueta</label>
            <div class="tag-row">
              <button
                v-for="tag in tagOptions"
                :key="tag.value"
                type="button"
                :class="['tag-btn', { active: form.tag === tag.value }]"
                @click="form.tag = form.tag === tag.value ? '' : tag.value"
              >
                {{ tag.label }}
              </button>
            </div>
          </div>

          <!-- Prioridad -->
          <div class="field">
            <label>Prioridad</label>
            <div class="tag-row">
              <button
                v-for="p in priorityOptions"
                :key="p.value"
                type="button"
                :class="['priority-btn', `prio-${p.value}`, { active: form.priority === p.value }]"
                @click="form.priority = p.value"
              >
                {{ p.label }}
              </button>
            </div>
          </div>

          <!-- Fecha límite -->
          <div class="field">
            <label>Fecha límite (opcional)</label>
            <input v-model="form.due_date" type="datetime-local" />
          </div>

          <!-- Botones -->
          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn-save" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              <span v-else>Guardar tarea</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../services/api.js'
import { useAuthStore } from '../stores/auth.js'

const emit = defineEmits(['close', 'created'])
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  text: '',
  subject: '',
  tag: '',
  due_date: '',
  priority: 'media',
})

const subjectSuggestions = [
  'Cálculo II', 'Programación', 'Base de Datos', 'Inteligencia Artificial',
  'Redes', 'Álgebra', 'Física', 'Estadística',
]

const tagOptions = [
  { value: 'Cálculo',  label: 'Cálculo' },
  { value: 'Prog',     label: 'Prog' },
  { value: 'BD',       label: 'BD' },
  { value: 'IA',       label: 'IA' },
  { value: 'Otro',     label: 'Otro' },
]

const priorityOptions = [
  { value: 'alta',  label: 'Alta' },
  { value: 'media', label: 'Media' },
  { value: 'baja',  label: 'Baja' },
]

async function submit() {
  loading.value = true
  try {
    const payload = {
      user_id: authStore.userId,
      text:    form.text,
      subject: form.subject || null,
      tag:     form.tag     || null,
      due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
      priority: form.priority,
    }
    const { data } = await api.post('/api/tasks/', payload)
    emit('created', data)
    emit('close')
  } catch (err) {
    console.error('Error al crear tarea:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  animation: slide-up 0.18s ease;
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.25rem 0;
}

.modal-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 14px;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: background 0.15s;
}
.close-btn:hover { background: var(--bg-hover); }

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.required { color: #e53e3e; }

.field input {
  padding: 9px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-md);
  background: var(--bg-page);
  color: var(--text-primary);
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  outline: none;
  transition: border-color 0.15s;
}
.field input:focus { border-color: var(--accent); }

.tag-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-btn {
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid var(--border-strong);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  font-family: 'DM Sans', sans-serif;
}
.tag-btn:hover  { background: var(--bg-hover); }
.tag-btn.active {
  background: var(--accent-light);
  border-color: rgba(29,158,117,0.4);
  color: var(--accent-dark);
  font-weight: 500;
}

.priority-btn {
  padding: 4px 14px;
  border-radius: 20px;
  border: 1px solid var(--border-strong);
  background: transparent;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  font-family: 'DM Sans', sans-serif;
  color: var(--text-secondary);
}
.priority-btn:hover { background: var(--bg-hover); }
.prio-alta.active  { background: #fee2e2; border-color: #e53e3e; color: #b91c1c; font-weight: 500; }
.prio-media.active { background: #fef3c7; border-color: #dd6b20; color: #92400e; font-weight: 500; }
.prio-baja.active  { background: #dbeafe; border-color: #3182ce; color: #1e3a5f; font-weight: 500; }

.modal-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 4px;
}

.btn-cancel {
  padding: 9px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-strong);
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-cancel:hover { background: var(--bg-hover); }

.btn-save {
  padding: 9px 18px;
  border-radius: var(--radius-md);
  border: none;
  background: var(--accent);
  color: white;
  font-size: 13px;
  font-weight: 600;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-save:hover    { background: var(--accent-dark); }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner {
  width: 13px;
  height: 13px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
