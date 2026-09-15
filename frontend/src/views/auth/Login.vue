<template>
  <main class="login-page">
    <div class="theme-switch" aria-label="Tema visual">
      <button type="button" :class="{ active: theme === 'light' }" @click="applyTheme('light')">Claro</button>
      <button type="button" :class="{ active: theme === 'dark' }" @click="applyTheme('dark')">Oscuro</button>
    </div>

    <section class="login-wrap" aria-label="Inicio de sesion">
      <header class="login-title">
        <span class="brand-mark">MV</span>
        <h1>Monitor Vial</h1>
      </header>

      <div class="login-card">
        <header class="form-head">
          <p class="section-kicker">Inicio de sesion</p>
          <h2>Entrar al panel</h2>
          <p>Usa tus credenciales asignadas para continuar.</p>
        </header>

        <form @submit.prevent="submit" class="form-body" novalidate>
          <div class="field" :class="{ 'is-active': emailFocused }">
            <label class="field-label" for="login-email">Correo electronico</label>
            <div class="field-row">
              <svg class="field-ico" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
              </svg>
              <input
                id="login-email"
                v-model="form.email"
                type="email"
                required
                autocomplete="email"
                class="field-input"
                placeholder="correo@institucion.gob.gt"
                @focus="emailFocused = true"
                @blur="emailFocused = false"
              />
            </div>
          </div>

          <div class="field" :class="{ 'is-active': passwordFocused }">
            <label class="field-label" for="login-password">Contrasena</label>
            <div class="field-row">
              <svg class="field-ico" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25z" />
              </svg>
              <input
                id="login-password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                class="field-input"
                placeholder="Tu contrasena"
                @focus="passwordFocused = true"
                @blur="passwordFocused = false"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="eye-btn"
                :aria-label="showPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'"
              >
                <svg v-if="!showPassword" class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
                </svg>
                <svg v-else class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="error-block" role="alert">
            <svg class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            {{ error }}
          </div>

          <div class="aux-row">
            <router-link to="/forgot-password" class="aux-link">Olvide mi contrasena</router-link>
          </div>

          <button type="submit" :disabled="loading" class="submit-btn">
            <svg v-if="loading" class="spinner icon-sm" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>{{ loading ? 'Verificando...' : 'Ingresar' }}</span>
            <svg v-if="!loading" class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12h15m0 0-6.75-6.75M19.5 12l-6.75 6.75" />
            </svg>
          </button>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()
const { theme, apply: applyTheme } = useTheme()

const form = ref({ email: '', password: '' })
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const emailFocused = ref(false)
const passwordFocused = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/api/auth/login', form.value)
    auth.setAuth(data)
    router.push(data.user.terms_accepted ? '/' : '/terminos')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Credenciales incorrectas'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  --page-bg: #f4f2ec;
  --panel: #fffdf8;
  --panel-soft: #ebe6d9;
  --ink: #17202a;
  --muted: #66707c;
  --faint: #a8adad;
  --line: #d8d2c4;
  --primary: #1e3a5f;
  --primary-strong: #143050;
  --accent: #b88746;
  --danger: #b42318;
  --danger-bg: #fff0ed;

  min-height: 100vh;
  background: var(--page-bg);
  color: var(--ink);
  display: grid;
  place-items: center;
  font-family: 'DM Sans', sans-serif;
  padding: 28px;
  position: relative;
}

:global(html.dark) .login-page {
  --page-bg: #0b1118;
  --panel: #111923;
  --panel-soft: #162230;
  --ink: #e9edf0;
  --muted: #8b97a5;
  --faint: #3b4856;
  --line: #263342;
  --primary: #6fa8dc;
  --primary-strong: #8dbde7;
  --accent: #d7a45a;
  --danger: #f97066;
  --danger-bg: #311815;
}

.theme-switch {
  position: absolute;
  top: 24px;
  right: 24px;
  display: inline-grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  min-height: 36px;
  padding: 4px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--panel);
}

.theme-switch button {
  min-width: 58px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.theme-switch button.active {
  background: var(--page-bg);
  color: var(--ink);
  box-shadow: inset 0 0 0 1px var(--line);
}

.theme-switch button:hover {
  color: var(--primary);
}

.theme-switch button:focus-visible,
.eye-btn:focus-visible,
.aux-link:focus-visible,
.submit-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

.login-wrap {
  width: min(430px, 100%);
}

.login-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
  text-align: center;
}

.brand-mark {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border: 1px solid var(--primary);
  background: var(--primary);
  color: #fff;
  border-radius: 8px;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  font-size: 22px;
}

.login-title h1 {
  margin: 0;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 48px;
  line-height: 0.95;
  color: var(--ink);
}

.login-card {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  padding: 34px;
  box-shadow: 0 24px 70px rgba(22, 32, 42, 0.1);
}

:global(html.dark) .login-card {
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.32);
}

.form-head {
  margin-bottom: 30px;
}

.section-kicker {
  margin: 0 0 10px;
  color: var(--accent);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0;
}

.form-head h2 {
  margin: 0 0 10px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 38px;
  line-height: 0.95;
  color: var(--ink);
}

.form-head p:last-child {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.6;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  color: var(--ink);
  font-weight: 600;
}

.field-row {
  min-height: 50px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: color-mix(in srgb, var(--panel) 88%, var(--panel-soft));
  padding: 0 14px;
  transition: border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
}

.field.is-active .field-row {
  border-color: var(--primary);
  background: var(--panel);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 13%, transparent);
}

.field-ico {
  width: 17px;
  height: 17px;
  color: var(--faint);
  flex: 0 0 auto;
}

.field.is-active .field-ico {
  color: var(--primary);
}

.field-input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
  font-size: 14px;
}

.field-input::placeholder {
  color: var(--faint);
}

.eye-btn {
  width: 30px;
  height: 30px;
  border: 0;
  background: transparent;
  color: var(--muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  flex: 0 0 auto;
}

.eye-btn:hover {
  color: var(--primary);
  background: var(--panel-soft);
}

.error-block {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid color-mix(in srgb, var(--danger) 30%, transparent);
  background: var(--danger-bg);
  color: var(--danger);
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 13px;
}

.aux-row {
  display: flex;
  justify-content: flex-end;
  margin-top: -2px;
}

.aux-link {
  color: var(--muted);
  font-size: 13px;
  text-decoration: none;
}

.aux-link:hover {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.submit-btn {
  width: 100%;
  min-height: 50px;
  border: 0;
  border-radius: 8px;
  background: var(--primary);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: transform 80ms ease, background 160ms ease, opacity 160ms ease;
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-strong);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.submit-btn:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.icon-sm {
  width: 16px;
  height: 16px;
}

.spinner {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 520px) {
  .login-page {
    padding: 18px;
  }

  .theme-switch {
    top: 16px;
    right: 16px;
  }

  .login-title h1 {
    font-size: 42px;
  }

  .login-card {
    padding: 26px 20px;
  }
}
</style>
