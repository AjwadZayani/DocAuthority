<script setup>
import { computed, onMounted, ref } from 'vue'
import { documentController } from '@/controllers/documentController'

const summary = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

const metrics = computed(() => {
  const byStatus = summary.value?.counts.byStatus ?? {}

  return [
    { label: 'Drafts', value: byStatus.DRAFT ?? 0, tone: 'warm' },
    { label: 'In Review', value: byStatus.IN_REVIEW ?? 0, tone: 'alert' },
    { label: 'Approved', value: byStatus.APPROVED ?? 0, tone: 'calm' },
    { label: 'Rejected', value: byStatus.REJECTED ?? 0, tone: 'muted' },
  ]
})

const activity = computed(() =>
  (summary.value?.reviewQueue ?? [])
    .slice(0, 3)
    .map(
      (document) =>
        `${document.name} is awaiting approval at ${document.sensitivityLabel} sensitivity.`,
    ),
)

onMounted(async () => {
  try {
    summary.value = await documentController.getDashboardSummary()
  } catch (error) {
    errorMessage.value = error.message || 'Unable to load dashboard data.'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <section class="page-grid">
    <div class="hero card">
      <p class="section-label">Today</p>
      <h3>Workflow health is steady, but the review queue needs attention.</h3>
      <p>
        Most activity is concentrated in Operations and Compliance. Prioritize in-review documents
        with restricted sensitivity to keep approval times down.
      </p>
      <p v-if="isLoading" class="status-message">Loading dashboard metrics...</p>
      <p v-else-if="errorMessage" class="status-message error-message">{{ errorMessage }}</p>
    </div>

    <div class="metrics">
      <article v-for="metric in metrics" :key="metric.label" :class="['metric-card', metric.tone]">
        <p>{{ metric.label }}</p>
        <strong>{{ metric.value }}</strong>
      </article>
    </div>

    <div class="card">
      <p class="section-label">Next Actions</p>
      <ul class="simple-list">
        <li>Review documents that have been waiting more than 48 hours.</li>
        <li>Check rejected documents with missing rejection reasons.</li>
        <li>Archive approved documents scheduled for retirement this week.</li>
      </ul>
    </div>

    <div class="card">
      <p class="section-label">Recent Activity</p>
      <ul class="simple-list">
        <li v-for="item in activity" :key="item">{{ item }}</li>
        <li v-if="!activity.length && !isLoading">No active review items found.</li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.page-grid {
  display: grid;
  gap: 1.25rem;
}

.hero h3 {
  margin: 0.35rem 0 0.75rem;
  font-size: 1.7rem;
}

.hero p:last-child {
  max-width: 60ch;
  color: #465467;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.metric-card,
.card {
  padding: 1.25rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
}

.metric-card p,
.section-label {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-card strong {
  display: block;
  margin-top: 0.45rem;
  font-size: 2rem;
}

.warm {
  border-color: rgba(196, 107, 40, 0.25);
}

.alert {
  border-color: rgba(180, 83, 9, 0.3);
}

.calm {
  border-color: rgba(14, 116, 144, 0.26);
}

.muted {
  border-color: rgba(100, 116, 139, 0.22);
}

.simple-list {
  margin: 0.8rem 0 0;
  padding-left: 1.1rem;
  color: #465467;
}

.simple-list li + li {
  margin-top: 0.7rem;
}

.status-message {
  margin-top: 1rem;
  color: #465467;
}

.error-message {
  color: #b91c1c;
}

@media (max-width: 900px) {
  .metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
