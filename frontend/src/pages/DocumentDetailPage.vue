<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { documentController } from '@/controllers/documentController'
import { useSession } from '@/stores/session'

const route = useRoute()
const session = useSession()

const document = ref(null)
const isLoading = ref(true)
const isApproving = ref(false)
const errorMessage = ref('')
const actionMessage = ref('')

const timelineEntries = computed(() => {
  if (!document.value) {
    return []
  }

  return [
    `Created: ${document.value.createdAtLabel}`,
    `Updated: ${document.value.updatedAtLabel}`,
    `Published: ${document.value.publishedAtLabel}`,
    `Archived: ${document.value.archivedAtLabel}`,
    `Deleted: ${document.value.deletedAtLabel}`,
  ]
})

const loadDocument = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    document.value = await documentController.getDocument(route.params.id)
  } catch (error) {
    errorMessage.value = error.message || 'Unable to load document details.'
  } finally {
    isLoading.value = false
  }
}

const handleApprove = async () => {
  if (!document.value || !session.user.value?.id) {
    return
  }

  isApproving.value = true
  actionMessage.value = ''
  errorMessage.value = ''

  try {
    await documentController.approveDocument(document.value.id, session.user.value.id)
    actionMessage.value = 'Document approved successfully.'
    await loadDocument()
  } catch (error) {
    errorMessage.value = error.message || 'Unable to approve document.'
  } finally {
    isApproving.value = false
  }
}

onMounted(loadDocument)
watch(() => route.params.id, loadDocument)
</script>

<template>
  <section class="detail-grid">
    <article class="panel primary">
      <p class="section-label">Document Detail</p>
      <p v-if="isLoading" class="status-message">Loading document...</p>
      <p v-else-if="errorMessage" class="status-message error-message">{{ errorMessage }}</p>
      <template v-else-if="document">
        <h3>{{ document.name }}</h3>
        <p class="lede">
          A central workspace for metadata, content review, and workflow actions backed by the
          document service.
        </p>

        <div class="content-preview">
          <h4>Content Preview</h4>
          <p>{{ document.content || 'No document content provided.' }}</p>
        </div>
      </template>
    </article>

    <article class="panel">
      <p class="section-label">Metadata</p>
      <dl v-if="document" class="meta-list">
        <div>
          <dt>Status</dt>
          <dd>{{ document.statusLabel }}</dd>
        </div>
        <div>
          <dt>Sensitivity</dt>
          <dd>{{ document.sensitivityLabel }}</dd>
        </div>
        <div>
          <dt>Owner</dt>
          <dd>{{ document.ownerLabel }}</dd>
        </div>
        <div>
          <dt>Department</dt>
          <dd>{{ document.departmentLabel }}</dd>
        </div>
      </dl>
    </article>

    <article class="panel">
      <p class="section-label">Timeline</p>
      <ul class="timeline">
        <li v-for="entry in timelineEntries" :key="entry">{{ entry }}</li>
      </ul>
    </article>

    <article class="panel">
      <p class="section-label">Actions</p>
      <p v-if="actionMessage" class="status-message success-message">{{ actionMessage }}</p>
      <div class="actions">
        <button
          type="button"
          class="primary"
          :disabled="isApproving || !document || document.status !== 'IN_REVIEW'"
          @click="handleApprove"
        >
          {{ isApproving ? 'Approving...' : 'Approve' }}
        </button>
        <button type="button">Reject</button>
        <button type="button">Archive</button>
      </div>
    </article>
  </section>
</template>

<style scoped>
.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr);
  gap: 1rem;
}

.panel {
  padding: 1.25rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
}

.primary {
  grid-row: span 2;
}

.section-label {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.panel h3 {
  margin: 0.45rem 0 0.75rem;
  font-size: 1.7rem;
}

.lede {
  color: #465467;
}

.content-preview {
  margin-top: 1.25rem;
  padding: 1rem;
  border-radius: 18px;
  background: #f8fafc;
}

.content-preview h4 {
  margin-top: 0;
}

.meta-list {
  margin: 0.85rem 0 0;
}

.meta-list div + div {
  margin-top: 0.85rem;
}

dt {
  font-size: 0.8rem;
  text-transform: uppercase;
  color: #64748b;
}

dd {
  margin: 0.2rem 0 0;
  font-weight: 600;
}

.timeline {
  margin: 0.85rem 0 0;
  padding-left: 1rem;
  color: #465467;
}

.timeline li + li {
  margin-top: 0.7rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.85rem;
}

.actions button {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 999px;
  background: #fff;
}

.actions .primary {
  border: 0;
  background: #c46b28;
  color: #fff;
}

.status-message {
  margin: 0.75rem 0 0;
  color: #465467;
}

.error-message {
  color: #b91c1c;
}

.success-message {
  color: #0f766e;
}

@media (max-width: 900px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .primary {
    grid-row: auto;
  }
}
</style>
