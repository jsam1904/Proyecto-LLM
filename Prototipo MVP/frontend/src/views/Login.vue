<template>
  <div class="auth-page">
    <div class="auth-card">
      <!-- Logo -->
      <div class="brand">
        <div class="brand-icon">
          <svg viewBox="0 0 16 16" fill="white" width="18" height="18">
            <path d="M8 2L10 7H15L11 10L13 15L8 12L3 15L5 10L1 7H6Z"/>
          </svg>
        </div>
        <span class="brand-name">StudyAI</span>
      </div>

      <h1>{{ isRegister ? 'Crear cuenta' : 'Bienvenido de vuelta' }}</h1>
      <p class="subtitle">
        {{ isRegister
          ? 'Crea tu cuenta para empezar a planificar con IA'
          : 'Inicia sesión para continuar estudiando' }}
      </p>

      <!-- Error -->
      <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

      <!-- Formulario -->
      <form @submit.prevent="submit">
        <div v-if="isRegister" class="field">
          <label>Nombre completo</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Tu nombre"
            required
            autocomplete="name"
          />
        </div>

        <div class="field">
          <label>Correo electrónico</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="correo@ejemplo.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="field">
          <label>Contraseña</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            required
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ isRegister ? 'Crear cuenta' : 'Iniciar sesión' }}</span>
        </button>
      </form>

      <p class="toggle-text">
        {{ isRegister ? '¿Ya tienes cuenta?' : '¿No tienes cuenta?' }}
        <button class="toggle-link" @click="toggleMode">
          {{ isRegister ? 'Iniciar sesión' : 'Regístrate' }}
        </button>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router   = useRouter()
const authStore = useAuthStore()

const isRegister = ref(false)
const loading    = ref(false)
const errorMsg   = ref('')

const form = reactive({ name: '', email: '', password: '' })

function toggleMode() {
  isRegister.value = !isRegister.value
  errorMsg.value   = ''
  form.name        = ''
  form.email       = ''
  form.password    = ''
}

async function submit() {
  loading.value  = true
  errorMsg.value = ''
  try {
    if (isRegister.value) {
      await authStore.register(form.name, form.email, form.password)
    } else {
      await authStore.login(form.email, form.password)
    }
    // replace en lugar de push para no dejar el /login en el historial
    await router.replace('/')
  } catch (err) {
    // Mostrar el mensaje de error del backend si existe
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') {
      errorMsg.value = detail
    } else if (err.response?.status === 422) {
      errorMsg.value = 'Datos inválidos. Verifica el formulario.'
    } else if (!err.response) {
      errorMsg.value = 'No se pudo conectar con el servidor. Intenta de nuevo.'
    } else {
      errorMsg.value = isRegister.value
        ? 'Error al crear la cuenta. Intenta de nuevo.'
        : 'Credenciales incorrectas. Verifica tu correo y contraseña.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: var(--bg-page);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.auth-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.5rem;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

h1 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.error-banner {
  background: #fee2e2;
  border: 1px solid #fca5a5;
  color: #b91c1c;
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 13px;
}

form {
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

.field input {
  padding: 10px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-md);
  background: var(--bg-page);
  color: var(--text-primary);
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  outline: none;
  transition: border-color 0.15s;
}

.field input:focus {
  border-color: var(--accent);
}

.submit-btn {
  margin-top: 4px;
  padding: 11px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover { background: var(--accent-dark); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.toggle-text {
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.toggle-link {
  background: none;
  border: none;
  color: var(--accent-dark);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}
</style>
