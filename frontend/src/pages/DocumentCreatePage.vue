<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { documentController } from '@/controllers/documentController'
import { useSession } from '@/stores/session'

const router = useRouter()
const session = useSession()

const isSubmitting = ref(false)
const errorMessage = ref('')

const form = reactive({
  name: '',
  content: '',
  sensitivity: 'INTERNAL',
  status: 'DRAFT',
})

const handleSubmit = async () => {
  if (!session.user.value?.id || !session.snapshot.value?.department_id) {
    errorMessage.value = 'Current user context is incomplete.'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const createdDocument = await documentController.createDocument({
      name: form.name,
      content: form.content,
      sensitivity: form.sensitivity,
      status: form.status,
      ownerId: session.user.value.id,
      departmentId: session.snapshot.value.department_id,
    })

    router.push({ name: 'document-detail', params: { id: createdDocument.id } })
  } catch (error) {
    errorMessage.value = error.message || 'Unable to create document.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="create-card">
    <p class="section-label">Create Document</p>
    <h3>Start a new controlled document.</h3>

    <form class="form-grid" @submit.prevent="handleSubmit">
      <label>
        <span>Name</span>
        <input v-model="form.name" type="text" required />
      </label>

      <label class="full-width">
        <span>Content</span>
        <textarea v-model="form.content" rows="10" required />
      </label>

      <label>
        <span>Sensitivity</span>
        <select v-model="form.sensitivity">
          <option value="PUBLIC">Public</option>
          <option value="INTERNAL">Internal</option>
          <option value="CONFIDENTIAL">Confidential</option>
          <option value="RESTRICTED">Restricted</option>
        </select>
      </label>

      <label>
        <span>Status</span>
        <select v-model="form.status">
          <option value="DRAFT">Draft</option>
          <option value="IN_REVIEW">In Review</option>
        </select>
      </label>

      <p v-if="errorMessage" class="error-message full-width">{{ errorMessage }}</p>

      <div class="actions full-width">
        <button type="submit" class="primary-action" :disabled="isSubmitting">
          {{ isSubmitting ? 'Creating...' : 'Create Document' }}
        </button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.create-card {
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

.create-card h3 {
  margin: 0.45rem 0 1.25rem;
  font-size: 1.7rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

label {
  display: grid;
  gap: 0.45rem;
}

span {
  font-size: 0.9rem;
  font-weight: 600;
}

input,
textarea,
select {
  padding: 0.9rem 1rem;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 16px;
  background: #fff;
  font: inherit;
}

textarea {
  resize: vertical;
}

.full-width {
  grid-column: 1 / -1;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.primary-action {
  padding: 0.85rem 1.15rem;
  border: 0;
  border-radius: 999px;
  background: #c46b28;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}

.error-message {
  margin: 0;
  color: #b91c1c;
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
