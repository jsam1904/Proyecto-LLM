<template>
  <div class="view">
    <header class="view-header">
      <h1>Asistente IA</h1>
      <p class="subtitle">Powered by OpenAI — responde preguntas académicas y ajusta tu plan</p>
    </header>

    <div class="chat-layout">
      <!-- Panel de chat principal -->
      <div class="chat-panel">
        <div class="messages" ref="messagesEl">
          <!-- Mensaje de bienvenida si no hay historial -->
          <div v-if="messages.length === 0 && !loadingHistory" class="welcome-msg">
            <div class="welcome-icon">🤖</div>
            <p>¡Hola, {{ authStore.userName }}! Soy tu asistente académico.<br/>
            Puedo ayudarte con dudas, técnicas de estudio y planificar tu semana.</p>
          </div>

          <div
            v-for="msg in messages"
            :key="msg.id"
            :class="['message', msg.role]"
          >
            <div v-if="msg.role === 'assistant'" class="msg-avatar">
              <svg viewBox="0 0 16 16" fill="white" width="12" height="12">
                <path d="M8 2L10 7H15L11 10L13 15L8 12L3 15L5 10L1 7H6Z"/>
              </svg>
            </div>
            <div class="msg-bubble">
              <div
                v-if="msg.role === 'assistant'"
                class="msg-md"
                v-html="renderMarkdown(msg.content)"
              ></div>
              <p v-else style="white-space: pre-wrap;">{{ msg.content }}</p>
              <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="isTyping" class="message assistant">
            <div class="msg-avatar">
              <svg viewBox="0 0 16 16" fill="white" width="12" height="12">
                <path d="M8 2L10 7H15L11 10L13 15L8 12L3 15L5 10L1 7H6Z"/>
              </svg>
            </div>
            <div class="msg-bubble typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <div class="input-area">
          <div class="quick-prompts">
            <button
              v-for="p in quickPrompts"
              :key="p"
              class="quick-btn"
              @click="sendQuick(p)"
              :disabled="isTyping"
            >{{ p }}</button>
          </div>
          <div class="input-row">
            <textarea
              v-model="inputText"
              placeholder="Escribe tu pregunta..."
              rows="1"
              @keydown.enter.exact.prevent="send"
            ></textarea>
            <button class="send-btn" @click="send" :disabled="!inputText.trim() || isTyping">
              <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16">
                <path d="M15 8L1 1l3 7-3 7 14-7z"/>
              </svg>
            </button>
          </div>
          <div class="input-footer">
            <p class="input-hint">Enter para enviar · Shift+Enter para nueva línea</p>
            <button class="clear-btn" @click="clearHistory" :disabled="messages.length === 0">
              Limpiar historial
            </button>
          </div>
        </div>
      </div>

      <!-- Panel de contexto -->
      <aside class="context-panel">
        <h3>Contexto activo</h3>

        <div class="context-item" v-if="nextExam">
          <span class="ctx-label">Examen próximo</span>
          <span class="ctx-val">{{ nextExam.subject }} — {{ nextExam.days_remaining }} días</span>
        </div>
        <div class="context-item" v-else>
          <span class="ctx-label">Examen próximo</span>
          <span class="ctx-val">Sin exámenes</span>
        </div>

        <div class="context-item">
          <span class="ctx-label">Mensajes en historial</span>
          <span class="ctx-val">{{ messages.length }} mensajes</span>
        </div>

        <h3 style="margin-top: 1.25rem;">Acciones rápidas</h3>
        <button class="action-btn" @click="sendQuick('Genera mi plan de estudio para esta semana')">
          Generar plan semanal ↗
        </button>
        <button class="action-btn" @click="sendQuick('Dame técnicas de estudio efectivas para exámenes')">
          Técnicas de estudio ↗
        </button>
        <button
          v-if="nextExam"
          class="action-btn"
          @click="sendQuick(`Necesito un plan de repaso para el examen de ${nextExam.subject} en ${nextExam.days_remaining} días`)"
        >
          Plan de repaso ↗
        </button>
        <button v-else class="action-btn" @click="sendQuick('Explícame cómo mejorar mi concentración al estudiar')">
          Mejorar concentración ↗
        </button>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import markdownItKatex from '@traptitech/markdown-it-katex'
import api from '../services/api.js'
import { useAuthStore } from '../stores/auth.js'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })
md.use(markdownItKatex, { throwOnError: false, errorColor: '#cc0000' })

function preprocessMath(text) {
  // \(...\) → $...$  (inline LaTeX que el AI usa pero el plugin no parsea)
  text = text.replace(/\\\((.+?)\\\)/gs, '$$$1$$')
  // \[...\] → $$...$$
  text = text.replace(/\\\[(.+?)\\\]/gs, '$$$$$1$$$$')
  // Eliminar duplicado: $fórmula$ inmediatamente seguida de $$fórmula$$ en línea siguiente
  // El AI genera ambas versiones; conservamos solo el bloque display ($$)
  text = text.replace(/\$([^$\n]+)\$[ \t]*\n[ \t]*\$\$([^$]+?)\$\$/g, (_m, _inline, display) => `$$${display}$$`)
  return text
}

function renderMarkdown(text) {
  return md.render(preprocessMath(text || ''))
}

const authStore = useAuthStore()
const messagesEl    = ref(null)
const inputText     = ref('')
const isTyping      = ref(false)
const loadingHistory = ref(true)
const messages      = ref([])
const nextExam      = ref(null)

const quickPrompts = [
  'Genera un plan de repaso',
  'Técnicas de estudio',
  'Explícame un tema',
]

// ── Helpers ───────────────────────────────────────────────────────
function formatTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('es-GT', {
    hour: '2-digit', minute: '2-digit',
  })
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

// ── Cargar historial ──────────────────────────────────────────────
async function fetchHistory() {
  loadingHistory.value = true
  try {
    const [histRes, examRes] = await Promise.all([
      api.get(`/api/chat/history/${authStore.userId}`),
      api.get(`/api/exams/${authStore.userId}/next`),
    ])
    messages.value = histRes.data
    nextExam.value  = examRes.data
    await scrollToBottom()
  } catch (err) {
    console.error('Error cargando historial:', err)
  } finally {
    loadingHistory.value = false
  }
}

// ── Enviar mensaje ────────────────────────────────────────────────
async function send() {
  const text = inputText.value.trim()
  if (!text || isTyping.value) return
  inputText.value = ''

  // Agregar mensaje del usuario localmente (sin esperar confirmación)
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: text,
    created_at: new Date().toISOString(),
  })
  await scrollToBottom()
  isTyping.value = true

  try {
    const { data } = await api.post('/api/chat/message', {
      user_id: authStore.userId,
      message: text,
    })
    messages.value.push({
      id: data.message_id,
      role: 'assistant',
      content: data.reply,
      created_at: new Date().toISOString(),
    })
  } catch (err) {
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: '⚠️ Error al conectar con el asistente. Verifica tu conexión e intenta de nuevo.',
      created_at: new Date().toISOString(),
    })
    console.error('Error en chat:', err)
  } finally {
    isTyping.value = false
    await scrollToBottom()
  }
}

async function sendQuick(text) {
  inputText.value = text
  await send()
}

// ── Limpiar historial ─────────────────────────────────────────────
async function clearHistory() {
  try {
    await api.delete(`/api/chat/history/${authStore.userId}`)
    messages.value = []
  } catch (err) {
    console.error('Error limpiando historial:', err)
  }
}

onMounted(fetchHistory)
</script>

<style scoped>
.view {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  height: 100vh;
  box-sizing: border-box;
}

.view-header h1 { font-size: 22px; font-weight: 600; }
.subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 3px; }

.chat-layout {
  display: grid;
  grid-template-columns: 1fr 240px;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

.chat-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.welcome-msg {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
}
.welcome-icon { font-size: 2.5rem; }

.message { display: flex; gap: 10px; align-items: flex-end; }
.message.user { flex-direction: row-reverse; }

.msg-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--accent);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.msg-bubble {
  max-width: 72%;
  padding: 10px 13px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.55;
}
.msg-bubble p { margin: 0; }

.msg-md { font-size: 13px; line-height: 1.6; }
.msg-md p { margin: 0 0 6px; }
.msg-md p:last-child { margin-bottom: 0; }
.msg-md ul, .msg-md ol { margin: 4px 0 6px 18px; padding: 0; }
.msg-md li { margin-bottom: 2px; }
.msg-md strong { font-weight: 600; }
.msg-md code {
  background: rgba(0,0,0,0.08);
  border-radius: 4px;
  padding: 1px 5px;
  font-size: 12px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.msg-md pre {
  background: rgba(0,0,0,0.06);
  border-radius: 6px;
  padding: 10px 12px;
  overflow-x: auto;
  margin: 6px 0;
}
.msg-md pre code { background: none; padding: 0; font-size: 12px; }
.msg-md .katex-display { margin: 10px 0; overflow-x: auto; text-align: center; }
.msg-md .katex { font-size: 1.05em; }
.msg-md .katex-display > .katex { font-size: 1.15em; }

.message.assistant .msg-bubble {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}
.message.user .msg-bubble {
  background: var(--accent);
  color: white;
  border-bottom-right-radius: 4px;
}

.msg-time {
  display: block;
  font-size: 10px;
  opacity: 0.55;
  margin-top: 4px;
}

.typing-indicator {
  display: flex; gap: 4px; align-items: center; padding: 12px 16px;
}
.typing-indicator span {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: bounce 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-5px); }
}

.input-area {
  border-top: 1px solid var(--border);
  padding: 12px;
}

.quick-prompts {
  display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap;
}
.quick-btn {
  font-size: 11px; padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid var(--border-strong);
  background: transparent; color: var(--text-secondary);
  cursor: pointer; transition: background 0.15s;
  font-family: 'DM Sans', sans-serif;
}
.quick-btn:hover:not(:disabled) { background: var(--bg-hover); color: var(--text-primary); }
.quick-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.input-row { display: flex; gap: 8px; align-items: flex-end; }
.input-row textarea {
  flex: 1;
  font-family: 'DM Sans', sans-serif; font-size: 13px;
  padding: 9px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-strong);
  background: var(--bg-page); color: var(--text-primary);
  resize: none; outline: none;
  transition: border-color 0.15s;
}
.input-row textarea:focus { border-color: var(--accent); }

.send-btn {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--accent); color: white;
  border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: background 0.15s;
}
.send-btn:hover { background: var(--accent-dark); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.input-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 5px;
}
.input-hint { font-size: 10px; color: var(--text-tertiary); margin: 0; }
.clear-btn {
  font-size: 11px; color: var(--text-tertiary);
  background: none; border: none; cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: color 0.15s;
}
.clear-btn:hover:not(:disabled) { color: #b91c1c; }
.clear-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* Context panel */
.context-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  display: flex; flex-direction: column; gap: 8px;
  overflow-y: auto;
}

.context-panel h3 {
  font-size: 11px; font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase; letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.context-item {
  display: flex; flex-direction: column; gap: 2px;
  padding: 8px 10px;
  background: var(--bg-hover);
  border-radius: var(--radius-sm);
}
.ctx-label { font-size: 11px; color: var(--text-secondary); }
.ctx-val   { font-size: 13px; font-weight: 500; color: var(--text-primary); }

.action-btn {
  width: 100%; text-align: left;
  font-size: 12px; padding: 8px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-strong);
  background: transparent; color: var(--text-secondary);
  cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: background 0.15s, color 0.15s;
}
.action-btn:hover {
  background: var(--accent-light);
  color: var(--accent-dark);
  border-color: rgba(29,158,117,0.3);
}
</style>
