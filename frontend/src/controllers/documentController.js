import { documentApi } from '@/api/documentApi'

const statusLabel = (status) => status?.replaceAll('_', ' ') ?? 'Unknown'

const formatInstant = (value) => {
  if (!value) {
    return 'Not set'
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

const normalizeDocument = (document) => ({
  ...document,
  statusLabel: statusLabel(document.status),
  sensitivityLabel: document.sensitivity ?? 'Unknown',
  ownerLabel: document.ownerName ?? document.ownerId ?? 'Unknown owner',
  departmentLabel: document.departmentName ?? document.departmentId ?? 'Unknown department',
  createdAtLabel: formatInstant(document.createdAt),
  updatedAtLabel: formatInstant(document.updatedAt),
  publishedAtLabel: formatInstant(document.publishedAt),
  archivedAtLabel: formatInstant(document.archivedAt),
  deletedAtLabel: formatInstant(document.deletedAt),
})

const listDocuments = async () => {
  const documents = await documentApi.listDocuments()
  return documents.map(normalizeDocument)
}

export const documentController = {
  listDocuments,

  async createDocument(payload) {
    const document = await documentApi.createDocument(payload)
    return normalizeDocument(document)
  },

  async getDocument(documentId) {
    const document = await documentApi.getDocumentById(documentId)
    return normalizeDocument(document)
  },

  async getDashboardSummary() {
    const documents = await listDocuments()

    const counts = documents.reduce(
      (summary, document) => {
        summary.total += 1
        summary.byStatus[document.status] = (summary.byStatus[document.status] ?? 0) + 1
        return summary
      },
      { total: 0, byStatus: {} },
    )

    const reviewQueue = documents.filter((document) => document.status === 'IN_REVIEW')

    return {
      documents,
      counts,
      reviewQueue,
    }
  },

  async getReviewQueue() {
    const documents = await listDocuments()
    return documents.filter((document) => document.status === 'IN_REVIEW')
  },

  approveDocument(documentId, actorId) {
    return documentApi.approveDocument(documentId, actorId)
  },
}
