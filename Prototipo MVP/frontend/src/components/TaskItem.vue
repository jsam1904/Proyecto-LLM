<template>
  <div :class="['task-item', { done: task.done }]">
    <button class="checkbox" @click="$emit('toggle', task.id)" :aria-label="task.done ? 'Marcar incompleto' : 'Marcar completo'">
      <svg v-if="task.done" viewBox="0 0 12 10" fill="none" width="10" height="10">
        <path d="M1 5l3 4L11 1" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
    <span class="task-text">{{ task.text }}</span>
    <span :class="['task-tag', tagClass]">{{ task.tag }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ task: Object })
defineEmits(['toggle'])
const tagMap = { 'Cálculo': 'tag-math', 'Prog': 'tag-prog', 'BD': 'tag-db', 'IA': 'tag-ia' }
const tagClass = computed(() => tagMap[props.task.tag] || 'tag-prog')
</script>

<style scoped>
.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  transition: background 0.12s;
}
.task-item:hover { background: var(--bg-hover); }
.task-item.done { opacity: 0.5; }

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

.task-text {
  flex: 1;
  font-size: 12.5px;
  color: var(--text-primary);
}
.task-item.done .task-text {
  text-decoration: line-through;
  color: var(--text-tertiary);
}

.task-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.tag-math { background: var(--tag-math-bg); color: var(--tag-math-tx); }
.tag-prog { background: var(--tag-prog-bg); color: var(--tag-prog-tx); }
.tag-db   { background: var(--tag-db-bg);   color: var(--tag-db-tx); }
.tag-ia   { background: var(--tag-ia-bg);   color: var(--tag-ia-tx); }
</style>
