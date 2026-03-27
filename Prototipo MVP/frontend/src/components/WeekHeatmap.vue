<template>
  <div>
    <div class="heatmap">
      <div v-for="day in data" :key="day.day" class="day-col">
        <div
          v-for="(h, i) in day.hours"
          :key="i"
          class="block"
          :class="intensityClass(h)"
          :title="`${day.day}: ${h}h`"
        ></div>
        <span class="day-label">{{ day.day }}</span>
      </div>
    </div>
    <div class="legend">
      <span class="leg-label">Poco</span>
      <div class="leg-block l0"></div>
      <div class="leg-block l1"></div>
      <div class="leg-block l2"></div>
      <div class="leg-block l3"></div>
      <span class="leg-label">Mucho</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ data: Array })
function intensityClass(h) {
  if (h === 0) return 'l0'
  if (h === 1) return 'l1'
  if (h === 2) return 'l2'
  return 'l3'
}
</script>

<style scoped>
.heatmap { display: flex; gap: 6px; margin-bottom: 12px; }
.day-col { display: flex; flex-direction: column; align-items: center; gap: 3px; flex: 1; }
.block { width: 100%; aspect-ratio: 1; border-radius: 3px; }
.l0 { background: var(--bg-hover); }
.l1 { background: #9FE1CB; }
.l2 { background: #5DCAA5; }
.l3 { background: #1D9E75; }
.day-label { font-size: 10px; color: var(--text-tertiary); margin-top: 2px; }
.legend { display: flex; align-items: center; gap: 4px; }
.leg-label { font-size: 10px; color: var(--text-tertiary); }
.leg-block { width: 10px; height: 10px; border-radius: 2px; }
</style>
