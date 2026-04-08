<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { documentController } from '@/controllers/documentController'

const reviewItems = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  try {
    reviewItems.value = await documentController.getReviewQueue()
  } catch (error) {
    errorMessage.value = error.message || 'Unable to load review queue.'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <section class="queue">
    <article class="queue-card lead">
      <p class="section-label">Approver Workbench</p>
      <h3>Documents waiting for a decision should be handled from here.</h3>
      <p>
        This page can later map directly to backend rules: `IN_REVIEW` status, actor role checks,
        and sensitivity clearance requirements.
      </p>
    </article>

    <article class="queue-card">
      <p class="section-label">Pending Items</p>
      <p v-if="isLoading">Loading review queue...</p>
      <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <ul>
        <li v-for="item in reviewItems" :key="item.id">
          <RouterLink :to="{ name: 'document-detail', params: { id: item.id } }" class="queue-link">
            {{ item.name }}
          </RouterLink>
          requires approval at {{ item.sensitivityLabel }} sensitivity.
        </li>
        <li v-if="!reviewItems.length && !isLoading">No documents are currently waiting for review.</li>
      </ul>
    </article>
  </section>
</template>

<style scoped>
.queue {
  display: grid;
  gap: 1rem;
}

.queue-card {
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

.lead h3 {
  margin: 0.45rem 0 0.75rem;
  font-size: 1.6rem;
}

ul {
  margin: 0.85rem 0 0;
  padding-left: 1rem;
  color: #465467;
}

li + li {
  margin-top: 0.7rem;
}

.queue-link {
  color: #9a4d10;
  font-weight: 600;
}

.error-message {
  color: #b91c1c;
}
</style>
