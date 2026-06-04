<template>
  <div :class="['task-item', { done: task.done }, priorityClass]">
    <button
      class="checkbox"
      @click="$emit('toggle', task.id)"
      :aria-label="task.done ? 'Marcar incompleto' : 'Marcar completo'"
    >
      <svg v-if="task.done" viewBox="0 0 12 10" fill="none" width="10" height="10">
        <path d="M1 5l3 4L11 1" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <div class="task-info">
      <span class="task-text">{{ task.text }}</span>
      <span v-if="task.subject" class="task-subject">{{ task.subject }}</span>
    </div>

    <span v-if="daysLabel" :class="['days-badge', daysUrgency]">{{ daysLabel }}</span>
    <span v-if="task.tag" :class="['task-tag', tagClass]">{{ task.tag }}</span>

    <button class="delete-btn" @click.stop="$emit('delete', task.id)" title="Eliminar">
      <svg viewBox="0 0 12 12" fill="currentColor" width="10" height="10">
        <path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ task: Object })
defineEmits(['toggle', 'delete'])

const tagMap   = { 'Cálculo': 'tag-math', 'Prog': 'tag-prog', 'BD': 'tag-db', 'IA': 'tag-ia' }
const tagClass = computed(() => tagMap[props.task.tag] || 'tag-prog')

const priorityClass = computed(() => {
  if (props.task.done) return ''
  const map = { alta: 'priority-alta', media: 'priority-media', baja: 'priority-baja' }
  return map[props.task.priority] || ''
})

const daysRemaining = computed(() => {
  if (!props.task.due_date || props.task.done) return null
  const diff = new Date(props.task.due_date) - new Date()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

const daysLabel = computed(() => {
  const d = daysRemaining.value
  if (d === null) return null
  if (d < 0) return 'Vencida'
  if (d === 0) return 'Hoy'
  if (d === 1) return '1 día'
  return `${d} días`
})

const daysUrgency = computed(() => {
  const d = daysRemaining.value
  if (d === null) return ''
  if (d <= 0) return 'days-overdue'
  if (d <= 2) return 'days-urgent'
  if (d <= 5) return 'days-warning'
  return 'days-ok'
})
</script>

<style scoped>
.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  border-left: 3px solid var(--border);
  transition: background 0.12s;
}
.task-item:hover { background: var(--bg-hover); }
.task-item.done { opacity: 0.55; }

.priority-alta  { border-left-color: #e53e3e; }
.priority-media { border-left-color: #dd6b20; }
.priority-baja  { border-left-color: #3182ce; }

.checkbox {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1.5px solid var(--border-strong);
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 0;
  transition: background 0.15s, border-color 0.15s;
}
.task-item.done .checkbox { background: var(--accent); border-color: var(--accent); }

.task-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.task-text {
  font-size: 12.5px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.task-item.done .task-text {
  text-decoration: line-through;
  color: var(--text-tertiary);
}

.task-subject {
  font-size: 10px;
  color: var(--text-tertiary);
}

.days-badge {
  font-size: 10px;
  padding: 2px 7px;
  border-radius: 10px;
  flex-shrink: 0;
  font-weight: 500;
}
.days-overdue { background: #fee2e2; color: #b91c1c; }
.days-urgent  { background: #fee2e2; color: #c53030; }
.days-warning { background: #fef3c7; color: #92400e; }
.days-ok      { background: #d1fae5; color: #065f46; }

.task-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.delete-btn {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.15s, background 0.15s, color 0.15s;
}
.task-item:hover .delete-btn { opacity: 1; }
.delete-btn:hover { background: #fee2e2; color: #b91c1c; }

.tag-math { background: var(--tag-math-bg); color: var(--tag-math-tx); }
.tag-prog { background: var(--tag-prog-bg); color: var(--tag-prog-tx); }
.tag-db   { background: var(--tag-db-bg);   color: var(--tag-db-tx); }
.tag-ia   { background: var(--tag-ia-bg);   color: var(--tag-ia-tx); }
</style>
