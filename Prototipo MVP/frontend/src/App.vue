<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">
          <svg viewBox="0 0 16 16" fill="white" width="14" height="14">
            <path d="M8 2L10 7H15L11 10L13 15L8 12L3 15L5 10L1 7H6Z"/>
          </svg>
        </div>
        <span>StudyAI</span>
      </div>

      <nav class="nav">
        <router-link to="/" class="nav-item">
          <IconGrid /> Dashboard
        </router-link>
        <router-link to="/plan" class="nav-item">
          <IconCalendar /> Plan de estudio
        </router-link>
        <router-link to="/assistant" class="nav-item">
          <IconChat /> Asistente IA
        </router-link>
        <router-link to="/progress" class="nav-item">
          <IconChart /> Progreso
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="avatar">MG</div>
          <div>
            <p class="user-name">María González</p>
            <p class="user-role">Estudiante</p>
          </div>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import IconGrid from './components/icons/IconGrid.vue'
import IconCalendar from './components/icons/IconCalendar.vue'
import IconChat from './components/icons/IconChat.vue'
import IconChart from './components/icons/IconChart.vue'
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  background: var(--bg-page);
  font-family: 'DM Sans', sans-serif;
}

.sidebar {
  width: 230px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2rem;
  padding-left: 4px;
}

.logo-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 13.5px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.router-link-active {
  background: var(--accent-light);
  color: var(--accent-dark);
  font-weight: 500;
}

.sidebar-footer {
  border-top: 1px solid var(--border);
  padding-top: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent);
  color: white;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.user-role {
  font-size: 11px;
  color: var(--text-secondary);
  margin: 0;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
