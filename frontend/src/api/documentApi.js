import { documentHttpClient } from '@/lib/httpClient'

export const documentApi = {
  listDocuments() {
    return documentHttpClient.get('/documents')
  },
  createDocument(payload) {
    return documentHttpClient.post('/documents', { body: payload })
  },
  getDocumentById(documentId) {
    return documentHttpClient.get(`/documents/${documentId}`)
  },
  approveDocument(documentId, actorId) {
    return documentHttpClient.post(`/documents/${documentId}/approve`, {
      query: { actorId },
    })
  },
}
