const trimTrailingSlash = (value) => value.replace(/\/+$/, '')

export const apiConfig = {
  documentBaseUrl: trimTrailingSlash(
    import.meta.env.VITE_DOCUMENT_API_URL ?? '/api/document',
  ),
  identityBaseUrl: trimTrailingSlash(
    import.meta.env.VITE_IDENTITY_API_URL ?? '/api/identity',
  ),
}
