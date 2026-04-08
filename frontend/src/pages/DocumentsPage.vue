<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { documentController } from '@/controllers/documentController'

const documents = ref([])
const isLoading = ref(true)
const errorMessage = ref('')
const searchTerm = ref('')

const filteredDocuments = computed(() => {
  const normalizedSearch = searchTerm.value.trim().toLowerCase()

  if (!normalizedSearch) {
    return documents.value
  }

  return documents.value.filter((document) =>
    [document.name, document.statusLabel, document.sensitivityLabel, document.ownerLabel, document.departmentLabel]
      .filter(Boolean)
      .some((value) => value.toLowerCase().includes(normalizedSearch)),
  )
})

onMounted(async () => {
  try {
    documents.value = await documentController.listDocuments()
  } catch (error) {
    errorMessage.value = error.message || 'Unable to load documents.'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <section class="stack">
    <div class="toolbar">
      <div class="filters">
        <input v-model="searchTerm" class="search-input" type="search" placeholder="Filter current results" />
      </div>
      <p>{{ filteredDocuments.length }} documents found</p>
    </div>

    <div class="table-card">
      <p v-if="isLoading" class="status-message">Loading documents...</p>
      <p v-else-if="errorMessage" class="status-message error-message">{{ errorMessage }}</p>

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Sensitivity</th>
            <th>Owner</th>
            <th>Department</th>
          </tr>
        </thead>
        <tbody v-if="!isLoading && !errorMessage">
          <tr v-for="document in filteredDocuments" :key="document.id">
            <td>
              <RouterLink :to="{ name: 'document-detail', params: { id: document.id } }" class="document-link">
                {{ document.name }}
              </RouterLink>
            </td>
            <td>{{ document.statusLabel }}</td>
            <td>{{ document.sensitivityLabel }}</td>
            <td>{{ document.ownerLabel }}</td>
            <td>{{ document.departmentLabel }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.stack {
  display: grid;
  gap: 1rem;
}

.toolbar,
.table-card {
  padding: 1.1rem 1.25rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}

.filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-input {
  padding: 0.65rem 0.9rem;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 999px;
  background: #fff;
}

.toolbar p {
  margin: 0;
  color: #465467;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.95rem 0.75rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.9);
  text-align: left;
}

thead th {
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #64748b;
}

tbody tr:last-child td {
  border-bottom: 0;
}

.document-link {
  color: #9a4d10;
  font-weight: 600;
}

.status-message {
  margin: 0 0 1rem;
  color: #465467;
}

.error-message {
  color: #b91c1c;
}

@media (max-width: 900px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .table-card {
    overflow-x: auto;
  }
}
</style>
