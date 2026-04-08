import { createRouter, createWebHistory } from 'vue-router'
import AppShell from '@/components/AppShell.vue'
import AuditPage from '@/pages/AuditPage.vue'
import DashboardPage from '@/pages/DashboardPage.vue'
import DocumentCreatePage from '@/pages/DocumentCreatePage.vue'
import DocumentDetailPage from '@/pages/DocumentDetailPage.vue'
import DocumentsPage from '@/pages/DocumentsPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import ReviewQueuePage from '@/pages/ReviewQueuePage.vue'
import { useSession } from '@/stores/session'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: {
        public: true,
      },
    },
    {
      path: '/',
      component: AppShell,
      meta: {
        requiresAuth: true,
      },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: DashboardPage,
          meta: {
            eyebrow: 'Overview',
            title: 'Dashboard',
          },
        },
        {
          path: 'documents',
          name: 'documents',
          component: DocumentsPage,
          meta: {
            eyebrow: 'Repository',
            title: 'Documents',
          },
        },
        {
          path: 'documents/new',
          name: 'document-create',
          component: DocumentCreatePage,
          meta: {
            eyebrow: 'Authoring',
            title: 'New Document',
          },
        },
        {
          path: 'documents/:id',
          name: 'document-detail',
          component: DocumentDetailPage,
          meta: {
            eyebrow: 'Workspace',
            title: 'Document Detail',
          },
        },
        {
          path: 'review-queue',
          name: 'review-queue',
          component: ReviewQueuePage,
          meta: {
            eyebrow: 'Approval Flow',
            title: 'Review Queue',
          },
        },
        {
          path: 'audit',
          name: 'audit',
          component: AuditPage,
          meta: {
            eyebrow: 'Observability',
            title: 'Audit Feed',
          },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const session = useSession()

  if (to.meta.requiresAuth && !session.isAuthenticated.value) {
    return { name: 'login' }
  }

  if (to.meta.public && session.isAuthenticated.value) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
