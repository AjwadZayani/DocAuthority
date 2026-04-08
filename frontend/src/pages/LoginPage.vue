<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authController } from '@/controllers/authController'
import { useSession } from '@/stores/session'

const router = useRouter()
const session = useSession()
const isSubmitting = ref(false)
const errorMessage = ref('')

const form = reactive({
  email: '',
  password: '',
})

const handleSubmit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const authSession = await authController.login({
      email: form.email,
      password: form.password,
    })

    session.login(authSession)
    router.push({ name: 'dashboard' })
  } catch (error) {
    errorMessage.value = error.message || 'Unable to sign in.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-hero">
      <p class="eyebrow">DocAuthority</p>
      <h1>Access controlled documents without losing workflow discipline.</h1>
      <p>
        Sign in before entering the document repository, review queue, and audit workspace.
      </p>
    </section>

    <section class="login-card">
      <p class="card-label">Sign In</p>
      <h2>Enter the workspace</h2>

      <form class="login-form" @submit.prevent="handleSubmit">
        <label>
          <span>Email</span>
          <input v-model="form.email" type="email" placeholder="approver@docauthority.local" required />
        </label>

        <label>
          <span>Password</span>
          <input v-model="form.password" type="password" placeholder="Enter your password" required />
        </label>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Signing In...' : 'Continue' }}
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  font-family:
    "Segoe UI",
    "Aptos",
    sans-serif;
  background:
    radial-gradient(circle at top left, rgba(230, 167, 86, 0.18), transparent 24%),
    linear-gradient(145deg, #f4efe6 0%, #fbf7f2 50%, #eef4f8 100%);
  color: #1f2a37;
}

.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(360px, 460px);
  gap: 2rem;
  align-items: center;
  padding: 2rem;
}

.login-hero,
.login-card {
  padding: 2rem;
  border-radius: 28px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
}

.login-hero {
  min-height: 440px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.1), rgba(15, 23, 42, 0.68)),
    linear-gradient(135deg, #d28b32, #243b53);
  color: #f8fafc;
}

.eyebrow,
.card-label {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.login-hero h1 {
  margin: 0.6rem 0 0.85rem;
  max-width: 12ch;
  font-size: clamp(2.5rem, 6vw, 4.75rem);
  line-height: 0.95;
}

.login-hero p:last-child {
  max-width: 48ch;
  margin: 0;
  color: rgba(248, 250, 252, 0.82);
}

.login-card {
  background: rgba(255, 255, 255, 0.88);
}

.login-card h2 {
  margin: 0.45rem 0 1.5rem;
  font-size: 2rem;
}

.login-form {
  display: grid;
  gap: 1rem;
}

.login-form label {
  display: grid;
  gap: 0.45rem;
}

.login-form span {
  font-size: 0.9rem;
  font-weight: 600;
}

.login-form input {
  padding: 0.95rem 1rem;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 16px;
  background: #fff;
}

.login-form button {
  margin-top: 0.4rem;
  padding: 0.95rem 1rem;
  border: 0;
  border-radius: 999px;
  background: #c46b28;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}

.login-form button:disabled {
  opacity: 0.72;
  cursor: wait;
}

.error-message {
  margin: 0;
  color: #b91c1c;
}

@media (max-width: 900px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 1.5rem;
  }

  .login-hero,
  .login-card {
    padding: 1.5rem;
  }

  .login-hero {
    min-height: 320px;
  }
}
</style>
