<template>
  <div class="view">
    <header class="view-header">
      <h1>Asistente IA</h1>
      <p class="subtitle">Powered by OpenAI — responde preguntas académicas y ajusta tu plan</p>
    </header>

    <div class="chat-layout">
      <div class="chat-panel">
        <div class="messages" ref="messagesEl">
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
              <p>{{ msg.content }}</p>
              <span class="msg-time">{{ msg.time }}</span>
            </div>
          </div>
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
          <p class="input-hint">Enter para enviar · Shift+Enter para nueva línea</p>
        </div>
      </div>

      <aside class="context-panel">
        <h3>Contexto activo</h3>
        <div class="context-item">
          <span class="ctx-label">Examen próximo</span>
          <span class="ctx-val">Cálculo II — Lunes</span>
        </div>
        <div class="context-item">
          <span class="ctx-label">Horas disponibles hoy</span>
          <span class="ctx-val">3h</span>
        </div>
        <div class="context-item">
          <span class="ctx-label">Tema débil detectado</span>
          <span class="ctx-val">Integrales definidas</span>
        </div>

        <h3 style="margin-top: 1.25rem;">Acciones rápidas</h3>
        <button class="action-btn" @click="sendQuick('Genera mi plan de estudio para esta semana')">
          Generar plan semanal ↗
        </button>
        <button class="action-btn" @click="sendQuick('Dame ejercicios de práctica de integrales definidas')">
          Ejercicios de práctica ↗
        </button>
        <button class="action-btn" @click="sendQuick('Explícame el Teorema Fundamental del Cálculo')">
          Explicar un tema ↗
        </button>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const messagesEl = ref(null)
const inputText = ref('')
const isTyping = ref(false)

const messages = ref([
  {
    id: 1,
    role: 'assistant',
    content: 'Hola María. Veo que tienes examen de Cálculo II en 3 días. ¿Quieres que te genere un plan de repaso intensivo o prefieres repasar algún tema específico?',
    time: '9:00 AM'
  }
])

const quickPrompts = [
  'Genera un plan de repaso',
  'Ejercicios de integrales',
  'Técnicas de estudio',
]

const cannedResponses = [
  'Entendido. Para integrales definidas, sugiero este orden: (1) Teorema fundamental — 30 min, (2) Técnicas de integración — 45 min, (3) Ejercicios de práctica — 45 min. ¿Empezamos?',
  'Perfecto. Recuerda usar la técnica de Pomodoro: 25 min de estudio, 5 min de descanso. Para Cálculo, resolver al menos 5 ejercicios diferentes es clave.',
  'He actualizado tu plan de estudio con este bloque. También recomiendo revisar los ejercicios del capítulo 7 que corresponden exactamente al tipo de preguntas del examen.',
  'Buena pregunta. El Teorema Fundamental del Cálculo conecta la derivada con la integral. En términos simples: si F es la antiderivada de f, entonces ∫(a,b) f(x)dx = F(b) - F(a).',
]
let cannedIdx = 0

function timeNow() {
  return new Date().toLocaleTimeString('es-GT', { hour: '2-digit', minute: '2-digit' })
}

async function send() {
  const text = inputText.value.trim()
  if (!text || isTyping.value) return
  inputText.value = ''
  messages.value.push({ id: Date.now(), role: 'user', content: text, time: timeNow() })
  await scrollToBottom()
  isTyping.value = true
  await new Promise(r => setTimeout(r, 1400))
  isTyping.value = false
  messages.value.push({
    id: Date.now() + 1,
    role: 'assistant',
    content: cannedResponses[cannedIdx % cannedResponses.length],
    time: timeNow()
  })
  cannedIdx++
  await scrollToBottom()
}

async function sendQuick(text) {
  inputText.value = text
  await send()
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}
</script>

<style scoped>
.view {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  height: 100vh;
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

.message {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.message.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.msg-bubble {
  max-width: 72%;
  padding: 10px 13px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.55;
  position: relative;
}

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
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
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
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.quick-btn {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid var(--border-strong);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.15s;
}

.quick-btn:hover { background: var(--bg-hover); color: var(--text-primary); }

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.input-row textarea {
  flex: 1;
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  padding: 9px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-strong);
  background: var(--bg-page);
  color: var(--text-primary);
  resize: none;
  outline: none;
  transition: border-color 0.15s;
}

.input-row textarea:focus { border-color: var(--accent); }

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s;
}

.send-btn:hover { background: var(--accent-dark); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.input-hint {
  font-size: 10px;
  color: var(--text-tertiary);
  margin-top: 5px;
}

.context-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.context-panel h3 {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.context-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 10px;
  background: var(--bg-hover);
  border-radius: var(--radius-sm);
}

.ctx-label { font-size: 11px; color: var(--text-secondary); }
.ctx-val { font-size: 13px; font-weight: 500; color: var(--text-primary); }

.action-btn {
  width: 100%;
  text-align: left;
  font-size: 12px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-strong);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.action-btn:hover { background: var(--accent-light); color: var(--accent-dark); border-color: rgba(29,158,117,0.3); }
</style>
