import { computed, ref } from 'vue'

const ACCESS_TOKEN_KEY = 'docauthority.accessToken'
const TOKEN_TYPE_KEY = 'docauthority.tokenType'
const USER_KEY = 'docauthority.user'
const SNAPSHOT_KEY = 'docauthority.userSnapshot'

const accessToken = ref(window.localStorage.getItem(ACCESS_TOKEN_KEY) ?? '')
const tokenType = ref(window.localStorage.getItem(TOKEN_TYPE_KEY) ?? '')
const user = ref(parseStoredJson(USER_KEY))
const snapshot = ref(parseStoredJson(SNAPSHOT_KEY))

function parseStoredJson(key) {
  const rawValue = window.localStorage.getItem(key)

  if (!rawValue) {
    return null
  }

  try {
    return JSON.parse(rawValue)
  } catch {
    window.localStorage.removeItem(key)
    return null
  }
}

function persistSession(nextSession) {
  accessToken.value = nextSession.accessToken
  tokenType.value = nextSession.tokenType
  user.value = nextSession.user
  snapshot.value = nextSession.snapshot

  window.localStorage.setItem(ACCESS_TOKEN_KEY, nextSession.accessToken)
  window.localStorage.setItem(TOKEN_TYPE_KEY, nextSession.tokenType)
  window.localStorage.setItem(USER_KEY, JSON.stringify(nextSession.user))
  window.localStorage.setItem(SNAPSHOT_KEY, JSON.stringify(nextSession.snapshot))
}

function clearSession() {
  accessToken.value = ''
  tokenType.value = ''
  user.value = null
  snapshot.value = null

  window.localStorage.removeItem(ACCESS_TOKEN_KEY)
  window.localStorage.removeItem(TOKEN_TYPE_KEY)
  window.localStorage.removeItem(USER_KEY)
  window.localStorage.removeItem(SNAPSHOT_KEY)
}

export function useSession() {
  return {
    accessToken: computed(() => accessToken.value),
    tokenType: computed(() => tokenType.value),
    user: computed(() => user.value),
    snapshot: computed(() => snapshot.value),
    isAuthenticated: computed(() => Boolean(accessToken.value && user.value)),
    login: persistSession,
    logout: clearSession,
  }
}
