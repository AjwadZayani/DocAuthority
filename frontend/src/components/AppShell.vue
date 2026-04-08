<script setup>
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useSession } from '@/stores/session'

const route = useRoute()
const router = useRouter()
const session = useSession()
const currentUser = computed(() => session.user.value)
const currentSnapshot = computed(() => session.snapshot.value)

const navigationItems = [
  { name: 'Dashboard', to: { name: 'dashboard' } },
  { name: 'Documents', to: { name: 'documents' } },
  { name: 'Review Queue', to: { name: 'review-queue' } },
  { name: 'Audit', to: { name: 'audit' } },
]

const pageMeta = computed(() => route.meta ?? {})

const handleLogout = () => {
  session.logout()
  router.push({ name: 'login' })
}

const handleCreateDocument = () => {
  router.push({ name: 'document-create' })
}
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <p class="eyebrow">DocAuthority</p>
        <h1>Document control, built for approvals.</h1>
      </div>

      <nav class="nav">
        <RouterLink
          v-for="item in navigationItems"
          :key="item.name"
          :to="item.to"
          class="nav-link"
          active-class="nav-link-active"
        >
          {{ item.name }}
        </RouterLink>
      </nav>

      <section class="sidebar-card">
        <p class="sidebar-label">Current user</p>
        <strong>{{ currentUser?.name ?? 'Unknown user' }}</strong>
        <p>{{ currentUser?.email ?? 'No email loaded' }}</p>
        <p class="sidebar-label secondary-label">Roles</p>
        <strong>{{ currentSnapshot?.roles?.join(', ') ?? 'No roles loaded' }}</strong>
        <p>Clearance: {{ currentSnapshot?.clearance?.join(', ') ?? 'No clearance loaded' }}</p>
      </section>
    </aside>

    <div class="content">
      <header class="topbar">
        <div>
          <p class="eyebrow">{{ pageMeta.eyebrow }}</p>
          <h2>{{ pageMeta.title }}</h2>
        </div>

        <div class="topbar-actions">
          <input class="search" type="search" placeholder="Search documents, owners, departments" />
          <button class="primary-action" type="button" @click="handleCreateDocument">New Document</button>
          <button class="secondary-action" type="button" @click="handleLogout">Log Out</button>
        </div>
      </header>

      <main class="main-panel">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(body) {
  margin: 0;
  font-family:
    "Segoe UI",
    "Aptos",
    sans-serif;
  background:
    radial-gradient(circle at top left, rgba(230, 167, 86, 0.18), transparent 26%),
    linear-gradient(135deg, #f4efe6 0%, #fbf7f2 45%, #f0f4f7 100%);
  color: #1f2a37;
}

:global(a) {
  color: inherit;
  text-decoration: none;
}

:global(button),
:global(input) {
  font: inherit;
}

:global(#app) {
  min-height: 100vh;
}

.shell {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 2rem;
  background: rgba(15, 23, 42, 0.92);
  color: #f8fafc;
}

.brand h1 {
  margin: 0.4rem 0 0;
  font-size: 1.9rem;
  line-height: 1.05;
}

.eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #d28b32;
}

.nav {
  display: grid;
  gap: 0.55rem;
}

.nav-link {
  padding: 0.9rem 1rem;
  border: 1px solid transparent;
  border-radius: 14px;
  color: rgba(248, 250, 252, 0.86);
  background: rgba(148, 163, 184, 0.08);
  transition:
    background-color 160ms ease,
    border-color 160ms ease,
    transform 160ms ease;
}

.nav-link:hover,
.nav-link-active {
  background: rgba(210, 139, 50, 0.18);
  border-color: rgba(210, 139, 50, 0.35);
  color: #fff;
  transform: translateX(2px);
}

.sidebar-card {
  margin-top: auto;
  padding: 1rem;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03));
}

.sidebar-label {
  margin: 0 0 0.35rem;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(248, 250, 252, 0.64);
}

.sidebar-card strong {
  display: block;
  margin-bottom: 0.35rem;
}

.sidebar-card p:last-child {
  margin-bottom: 0;
  color: rgba(248, 250, 252, 0.75);
}

.secondary-label {
  margin-top: 1rem;
}

.content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  align-items: center;
  padding: 2rem 2rem 1.25rem;
}

.topbar h2 {
  margin: 0.35rem 0 0;
  font-size: 2rem;
}

.topbar-actions {
  display: flex;
  gap: 0.9rem;
  align-items: center;
}

.search {
  width: min(100%, 340px);
  padding: 0.85rem 1rem;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
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

.secondary-action {
  padding: 0.85rem 1.15rem;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: #1f2a37;
  cursor: pointer;
}

.main-panel {
  padding: 0 2rem 2rem;
}

@media (max-width: 900px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    gap: 1.25rem;
    padding: 1.5rem;
  }

  .sidebar-card {
    margin-top: 0;
  }

  .topbar {
    flex-direction: column;
    align-items: stretch;
    padding: 1.5rem;
  }

  .topbar-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .main-panel {
    padding: 0 1.5rem 1.5rem;
  }
}
</style>
