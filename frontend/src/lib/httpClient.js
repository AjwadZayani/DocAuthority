import { apiConfig } from '@/config/api'

const buildUrl = (baseUrl, path, query) => {
  const url = new URL(`${baseUrl}${path}`, window.location.origin)

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.set(key, value)
      }
    })
  }

  return url.toString()
}

const parseResponse = async (response) => {
  const contentType = response.headers.get('content-type') ?? ''

  if (contentType.includes('application/json')) {
    return response.json()
  }

  return response.text()
}

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

export const createHttpClient = (baseUrl, authTokenResolver) => {
  const request = async (path, options = {}) => {
    const headers = new Headers(options.headers ?? {})
    const token = options.authToken ?? authTokenResolver?.()

    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }

    if (options.body !== undefined) {
      headers.set('Content-Type', 'application/json')
    }

    const response = await fetch(buildUrl(baseUrl, path, options.query), {
      method: options.method ?? 'GET',
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    })

    const data = await parseResponse(response)

    if (!response.ok) {
      const message =
        typeof data === 'object' && data !== null && 'error' in data ? data.error : response.statusText

      throw new ApiError(message || 'Request failed', response.status, data)
    }

    return data
  }

  return {
    get: (path, options) => request(path, { ...options, method: 'GET' }),
    post: (path, options) => request(path, { ...options, method: 'POST' }),
    patch: (path, options) => request(path, { ...options, method: 'PATCH' }),
    put: (path, options) => request(path, { ...options, method: 'PUT' }),
    delete: (path, options) => request(path, { ...options, method: 'DELETE' }),
  }
}

export const documentHttpClient = createHttpClient(apiConfig.documentBaseUrl)
export const identityHttpClient = createHttpClient(apiConfig.identityBaseUrl, () =>
  window.localStorage.getItem('docauthority.accessToken'),
)
