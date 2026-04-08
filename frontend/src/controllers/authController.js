import { identityApi } from '@/api/identityApi'

export const authController = {
  async login(credentials) {
    const result = await identityApi.login(credentials)
    const snapshot = await identityApi.getUserSnapshot(result.user.id, result.access_token)

    return {
      accessToken: result.access_token,
      tokenType: result.token_type,
      user: result.user,
      snapshot,
    }
  },
}
