<template>
  <div class="view">
    <header class="view-header">
      <div>
        <h1>Repaso</h1>
        <p class="subtitle">Genera preguntas, fichas o cuestionarios con IA sobre cualquier tema.</p>
      </div>
    </header>

    <!-- Formulario de generación -->
    <div class="card config-card">
      <div class="config-row">
        <div class="field">
          <label>Tema de repaso</label>
          <input
            v-model="topic"
            type="text"
            placeholder="Ej: Derivadas parciales, Redes TCP/IP, Álgebra relacional..."
            @keyup.enter="generate"
          />
        </div>

        <div class="field field-sm">
          <label>Tipo</label>
          <div class="type-row">
            <button
              v-for="t in tipoOptions"
              :key="t.value"
              :class="['type-btn', { active: tipo === t.value }]"
              @click="tipo = t.value"
              type="button"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <div class="field field-xs">
          <label>Cantidad</label>
          <select v-model="numItems">
            <option v-for="n in [3,5,8,10]" :key="n" :value="n">{{ n }}</option>
          </select>
        </div>

        <button class="btn-generate" @click="generate" :disabled="loading || !topic.trim()">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Generar</span>
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-msg">{{ error }}</div>

    <!-- Resultados: Preguntas abiertas -->
    <template v-if="result && result.tipo === 'preguntas'">
      <div class="results-header">
        <h2>Preguntas de repaso — {{ result.tema }}</h2>
        <button class="btn-reset" @click="resetAnswers">Reiniciar respuestas</button>
      </div>
      <div class="items-grid">
        <div
          v-for="(item, i) in result.items"
          :key="i"
          :class="['item-card', { revealed: revealed[i] }]"
        >
          <div class="item-num">{{ i + 1 }}</div>
          <p class="item-question">{{ item.pregunta }}</p>
          <div v-if="revealed[i]" class="item-answer">
            <span class="answer-label">Respuesta</span>
            <p>{{ item.respuesta }}</p>
          </div>
          <button
            v-else
            class="btn-reveal"
            @click="revealed[i] = true"
          >
            Ver respuesta
          </button>
        </div>
      </div>
    </template>

    <!-- Resultados: Fichas (flashcards) -->
    <template v-if="result && result.tipo === 'fichas'">
      <div class="results-header">
        <h2>Fichas de estudio — {{ result.tema }}</h2>
        <button class="btn-reset" @click="resetAnswers">Voltear todo</button>
      </div>
      <div class="items-grid">
        <div
          v-for="(item, i) in result.items"
          :key="i"
          :class="['flashcard', { flipped: revealed[i] }]"
          @click="revealed[i] = !revealed[i]"
        >
          <div class="flashcard-inner">
            <div class="flashcard-front">
              <span class="fc-label">Concepto</span>
              <p>{{ item.frente }}</p>
            </div>
            <div class="flashcard-back">
              <span class="fc-label">Definición</span>
              <p>{{ item.reverso }}</p>
            </div>
          </div>
        </div>
      </div>
      <p class="hint">Haz clic en una ficha para voltearla</p>
    </template>

    <!-- Resultados: Cuestionario de opción múltiple -->
    <template v-if="result && result.tipo === 'cuestionario'">
      <div class="results-header">
        <h2>Cuestionario — {{ result.tema }}</h2>
        <span class="score-badge" v-if="quizSubmitted">
          {{ quizScore }} / {{ result.items.length }} correctas
        </span>
        <button v-if="quizSubmitted" class="btn-reset" @click="resetQuiz">Reintentar</button>
      </div>
      <div class="quiz-list">
        <div
          v-for="(item, i) in result.items"
          :key="i"
          :class="['quiz-item', { submitted: quizSubmitted }]"
        >
          <p class="quiz-question"><span class="item-num">{{ i + 1 }}</span> {{ item.pregunta }}</p>
          <div class="quiz-options">
            <button
              v-for="(opt, j) in item.opciones"
              :key="j"
              :class="['quiz-opt', optionClass(i, opt, item.correcta)]"
              @click="!quizSubmitted && selectAnswer(i, opt)"
              :disabled="quizSubmitted"
            >
              {{ opt }}
            </button>
          </div>
          <p v-if="quizSubmitted" class="quiz-explanation">{{ item.explicacion }}</p>
        </div>
      </div>
      <div class="quiz-footer" v-if="!quizSubmitted">
        <button
          class="btn-generate"
          :disabled="Object.keys(answers).length < result.items.length"
          @click="submitQuiz"
        >
          Corregir
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../services/api.js'

const topic    = ref('')
const tipo     = ref('preguntas')
const numItems = ref(5)
const loading  = ref(false)
const error    = ref(null)
const result   = ref(null)
const revealed = reactive({})
const answers  = reactive({})
const quizSubmitted = ref(false)
const quizScore     = ref(0)

const tipoOptions = [
  { value: 'preguntas',    label: 'Preguntas' },
  { value: 'fichas',       label: 'Fichas' },
  { value: 'cuestionario', label: 'Cuestionario' },
]

async function generate() {
  if (!topic.value.trim()) return
  loading.value = true
  error.value   = null
  result.value  = null
  Object.keys(revealed).forEach(k => delete revealed[k])
  Object.keys(answers).forEach(k => delete answers[k])
  quizSubmitted.value = false
  quizScore.value     = 0

  try {
    const { data } = await api.post('/api/repaso/generate', {
      topic: topic.value.trim(),
      tipo:  tipo.value,
      num_items: numItems.value,
    })
    result.value = data
  } catch (err) {
    error.value = 'Error al generar el repaso. Intenta de nuevo.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function resetAnswers() {
  Object.keys(revealed).forEach(k => delete revealed[k])
}

function selectAnswer(i, opt) {
  answers[i] = opt
}

function optionClass(i, opt, correcta) {
  if (!quizSubmitted.value) {
    return answers[i] === opt ? 'selected' : ''
  }
  const letter = opt.charAt(0)
  if (letter === correcta) return 'correct'
  if (answers[i] === opt && letter !== correcta) return 'wrong'
  return ''
}

function submitQuiz() {
  quizSubmitted.value = true
  let score = 0
  result.value.items.forEach((item, i) => {
    if (answers[i] && answers[i].charAt(0) === item.correcta) score++
  })
  quizScore.value = score
}

function resetQuiz() {
  Object.keys(answers).forEach(k => delete answers[k])
  quizSubmitted.value = false
  quizScore.value     = 0
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

.view-header { display: flex; justify-content: space-between; align-items: flex-start; }
h1 { font-size: 22px; font-weight: 600; color: var(--text-primary); }
.subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 3px; }

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
}

.config-card { }

.config-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  min-width: 180px;
}
.field-sm { flex: 0 0 auto; min-width: 0; }
.field-xs { flex: 0 0 80px; min-width: 0; }

.field label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.field input, .field select {
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
.field input:focus, .field select:focus { border-color: var(--accent); }

.type-row { display: flex; gap: 5px; }
.type-btn {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid var(--border-strong);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
  white-space: nowrap;
}
.type-btn:hover { background: var(--bg-hover); }
.type-btn.active {
  background: var(--accent-light);
  border-color: rgba(29,158,117,0.4);
  color: var(--accent-dark);
  font-weight: 500;
}

.btn-generate {
  padding: 9px 20px;
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
  white-space: nowrap;
  align-self: flex-end;
}
.btn-generate:hover    { background: var(--accent-dark); }
.btn-generate:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner {
  width: 13px;
  height: 13px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-msg {
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: var(--radius-md);
  padding: 10px 14px;
  font-size: 13px;
  color: #b91c1c;
}

.results-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.results-header h2 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  margin: 0;
}

.btn-reset {
  font-size: 12px;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-strong);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.15s;
}
.btn-reset:hover { background: var(--bg-hover); }

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.item-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent-light);
  color: var(--accent-dark);
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-question {
  font-size: 13px;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.5;
}

.item-answer {
  background: var(--accent-light);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  font-size: 12.5px;
  color: var(--accent-dark);
}
.answer-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 3px;
  opacity: 0.7;
}

.btn-reveal {
  margin-top: auto;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  border: 1px dashed rgba(29,158,117,0.4);
  background: transparent;
  color: var(--accent-dark);
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.15s;
}
.btn-reveal:hover { background: var(--accent-light); }

/* Flashcards */
.flashcard {
  height: 160px;
  cursor: pointer;
  perspective: 800px;
}
.flashcard-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.45s;
  transform-style: preserve-3d;
}
.flashcard.flipped .flashcard-inner { transform: rotateY(180deg); }

.flashcard-front, .flashcard-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border-radius: var(--radius-lg);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
}
.flashcard-front {
  background: var(--bg-surface);
  border: 1px solid var(--border);
}
.flashcard-back {
  background: var(--accent-light);
  border: 1px solid rgba(29,158,117,0.2);
  transform: rotateY(180deg);
}
.fc-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-tertiary);
}
.flashcard-front p { font-size: 13px; font-weight: 500; color: var(--text-primary); margin: 0; }
.flashcard-back p  { font-size: 12.5px; color: var(--accent-dark); margin: 0; line-height: 1.5; }

.hint {
  font-size: 11px;
  color: var(--text-tertiary);
  text-align: center;
}

/* Cuestionario */
.quiz-list { display: flex; flex-direction: column; gap: 16px; }

.quiz-item {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quiz-question {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quiz-opt {
  text-align: left;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-strong);
  background: var(--bg-page);
  color: var(--text-primary);
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  transition: all 0.15s;
}
.quiz-opt:hover:not(:disabled) { background: var(--bg-hover); }
.quiz-opt.selected { background: var(--accent-light); border-color: rgba(29,158,117,0.4); color: var(--accent-dark); }
.quiz-opt.correct  { background: #d1fae5; border-color: #34d399; color: #065f46; font-weight: 500; }
.quiz-opt.wrong    { background: #fee2e2; border-color: #fca5a5; color: #b91c1c; }
.quiz-opt:disabled { cursor: default; }

.quiz-explanation {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-hover);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  margin: 0;
}

.score-badge {
  font-size: 13px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  background: var(--accent-light);
  color: var(--accent-dark);
}

.quiz-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
