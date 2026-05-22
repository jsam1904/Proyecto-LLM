<template>
  <div class="metric-card">
    <p class="label">{{ label }}</p>
    <p class="value">{{ value }}<span v-if="unit" class="unit">{{ unit }}</span></p>
    <p class="trend">{{ trend }}</p>
  </div>
</template>

<script setup>
defineProps({ label: String, value: [String, Number], unit: String, trend: String })
</script>

<style scoped>
.metric-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.125rem;
}
.label { font-size: 11px; color: var(--text-secondary); margin-bottom: 6px; }
.value { font-size: 22px; font-weight: 600; color: var(--text-primary); line-height: 1.1; }
.unit { font-size: 14px; font-weight: 400; color: var(--text-secondary); }
.trend { font-size: 11px; color: var(--text-tertiary); margin-top: 5px; }
</style>
