import { identityHttpClient } from '@/lib/httpClient'

export const identityApi = {
  login(credentials) {
    return identityHttpClient.post('/auth/login', { body: credentials })
  },
  getUserSnapshot(userId, accessToken) {
    return identityHttpClient.get(`/users/${userId}/snapshot`, {
      authToken: accessToken,
    })
  },
}
