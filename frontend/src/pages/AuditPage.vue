<script setup>
const auditEvents = [
  { time: '08:42', event: 'Document approved', subject: 'Quarterly Procurement Policy' },
  { time: '09:15', event: 'Sensitivity changed', subject: 'Vendor Security Standard' },
  { time: '10:03', event: 'Document deleted', subject: 'Legacy Travel SOP' },
]
</script>

<template>
  <section class="audit-card">
    <p class="section-label">Audit Feed</p>
    <h3>System events and document actions can surface here.</h3>

    <div class="feed">
      <article v-for="entry in auditEvents" :key="`${entry.time}-${entry.subject}`" class="event">
        <p>{{ entry.time }}</p>
        <div>
          <strong>{{ entry.event }}</strong>
          <span>{{ entry.subject }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.audit-card {
  padding: 1.25rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
}

.section-label {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.audit-card h3 {
  margin: 0.45rem 0 1rem;
  font-size: 1.6rem;
}

.feed {
  display: grid;
  gap: 0.75rem;
}

.event {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 0.75rem;
  padding: 0.9rem 0;
  border-top: 1px solid rgba(226, 232, 240, 0.9);
}

.event:first-child {
  border-top: 0;
}

.event p,
.event span {
  margin: 0;
  color: #64748b;
}

.event strong {
  display: block;
  margin-bottom: 0.2rem;
}
</style>
