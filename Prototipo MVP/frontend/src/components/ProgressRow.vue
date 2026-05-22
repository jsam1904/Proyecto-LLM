<template>
  <div class="progress-row">
    <div class="label-row">
      <span class="subject-name">{{ subject.name }}</span>
      <span class="pct">{{ subject.pct }}%</span>
    </div>
    <div class="bar-track">
      <div class="bar-fill" :style="{ width: subject.pct + '%', background: subject.color }"></div>
    </div>
    <span class="hours">{{ subject.hours }}h este mes</span>
  </div>
</template>

<script setup>
defineProps({ subject: Object })
</script>

<style scoped>
.progress-row { display: flex; flex-direction: column; gap: 5px; }
.label-row { display: flex; justify-content: space-between; }
.subject-name { font-size: 13px; color: var(--text-primary); }
.pct { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.bar-track { height: 8px; background: var(--bg-hover); border-radius: 10px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 10px; transition: width 0.6s ease; }
.hours { font-size: 11px; color: var(--text-tertiary); }
</style>
