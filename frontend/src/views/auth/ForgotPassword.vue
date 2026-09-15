<template>
  <div class="auth-root">
    <div class="noise" aria-hidden="true"></div>

    <main class="center-panel">
      <!-- Back link -->
      <router-link to="/login" class="back-link">
        <svg class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
        </svg>
        Volver al inicio de sesiÃ³n
      </router-link>

      <div class="card">
        <!-- Brand header -->
        <div class="card-brand">
          <div class="brand-chips">
            <div class="inst-chip">CR</div>
            <div class="inst-chip inst-chip--dim">SSI</div>
          </div>
          <span class="brand-name">Monitor Vial</span>
        </div>

        <!-- Success state -->
        <div v-if="sent" class="success-body">
          <div class="success-icon-wrap">
            <svg class="success-icon" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div class="eyebrow eyebrow--success">SOLICITUD ENVIADA</div>
          <h1 class="form-title">Revisa tu correo</h1>
          <p class="form-sub">
            Enviamos instrucciones de recuperaciÃ³n a
            <strong class="email-highlight">{{ form.email }}</strong>
          </p>
          <p class="notice">
            Si no recibes el correo, contacta al administrador del sistema.
          </p>
          <router-link to="/login" class="submit-btn submit-btn--link">
            Volver al inicio de sesiÃ³n
          </router-link>
        </div>

        <!-- Form state -->
        <template v-else>
          <header class="form-head">
            <div class="eyebrow">RECUPERACIÃ“N DE ACCESO</div>
            <h1 class="form-title">Recuperar contraseÃ±a</h1>
            <p class="form-sub">Ingresa tu correo y te enviaremos instrucciones para recuperar el acceso.</p>
          </header>

          <form @submit.prevent="submit" class="form-body" novalidate>
            <div class="field" :class="{ 'is-active': emailFocused }">
              <label class="field-label" for="fp-email">CORREO ELECTRÃ“NICO</label>
              <div class="field-row">
                <svg class="field-ico" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"/>
                </svg>
                <input id="fp-email" v-model="form.email" type="email" required autocomplete="email"
                       class="field-input" placeholder="correo@ejemplo.com"
                       @focus="emailFocused = true" @blur="emailFocused = false" />
              </div>
            </div>

            <button type="submit" :disabled="loading" class="submit-btn">
              <svg v-if="loading" class="spinner icon-sm" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              <span>{{ loading ? 'Enviando...' : 'Enviar instrucciones' }}</span>
              <svg v-if="!loading" class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12h15m0 0l-6.75-6.75M19.5 12l-6.75 6.75"/>
              </svg>
            </button>
          </form>
        </template>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({ email: '' })
const loading = ref(false)
const sent = ref(false)
const emailFocused = ref(false)

async function submit() {
  loading.value = true
  await new Promise((r) => setTimeout(r, 800))
  sent.value = true
  loading.value = false
}
</script>

<style scoped>
.auth-root {
  --bg:        #F5F7FA;
  --surface:   #FFFFFF;
  --border:    #DDE3ED;
  --border-hi: #B8C7D9;
  --accent:    #1E3A5F;
  --accent-hi: #254880;
  --accent-dim:rgba(30,58,95,.07);
  --green:     #16A34A;
  --t1:        #0F1923;
  --t2:        #6B7A8D;
  --t3:        #C2CDD9;
  --fd: 'Barlow Condensed', sans-serif;
  --fb: 'DM Sans', sans-serif;
  --fm: 'JetBrains Mono', monospace;

  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  font-family: var(--fb);
  padding: 32px 16px;
  position: relative;
}

.noise {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  opacity: 0.015; mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 300px;
}

/* back link */
.back-link {
  position: absolute; top: 28px; left: 28px;
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; font-weight: 400; color: var(--t2);
  text-decoration: none; transition: color 150ms;
  font-family: var(--fm); letter-spacing: .04em; text-transform: uppercase;
}

.back-link:hover { color: var(--accent); }
.back-link:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }

/* center panel */
.center-panel {
  position: relative; z-index: 1;
  width: 100%; max-width: 440px;
}

/* card */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 1px 3px rgba(30,58,95,.04), 0 8px 24px rgba(30,58,95,.06);
}

/* brand header */
.card-brand {
  display: flex; align-items: center; gap: 12px; margin-bottom: 32px;
}

.brand-chips { display: flex; gap: 8px; }

.inst-chip {
  width: 36px; height: 36px; border-radius: 6px;
  border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--fm); font-size: 9px; font-weight: 600;
  letter-spacing: .08em; color: var(--accent); background: var(--accent-dim);
}

.inst-chip--dim { color: var(--t2); background: transparent; }

.brand-name { font-size: 13px; color: var(--t2); font-weight: 400; }

/* form header */
.form-head { margin-bottom: 28px; }

.eyebrow {
  font-family: var(--fm); font-size: 9px; font-weight: 500;
  letter-spacing: .18em; color: var(--accent); margin-bottom: 10px;
}

.eyebrow--success { color: var(--green); }

.form-title {
  font-family: var(--fd); font-size: 32px; font-weight: 700;
  color: var(--t1); margin: 0 0 8px; line-height: 1; letter-spacing: -.01em;
}

.form-sub { font-size: 13px; font-weight: 300; color: var(--t2); margin: 0; line-height: 1.6; }

/* form body */
.form-body { display: flex; flex-direction: column; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 6px; }

.field-label {
  font-family: var(--fm); font-size: 9px; font-weight: 500;
  letter-spacing: .14em; color: var(--t2); transition: color 200ms;
}

.field.is-active .field-label { color: var(--accent); }

.field-row {
  display: flex; align-items: center; gap: 12px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 6px; padding: 12px 14px;
  transition: border-color 200ms, background 200ms;
}

.field.is-active .field-row { border-color: var(--accent); background: var(--accent-dim); }

.field-ico { width: 15px; height: 15px; color: var(--t3); flex-shrink: 0; transition: color 200ms; }
.field.is-active .field-ico { color: var(--accent); }

.field-input {
  flex: 1; border: none; background: transparent; outline: none;
  font-family: var(--fb); font-size: 14px; color: var(--t1);
}

.field-input::placeholder { color: var(--t3); }

/* submit */
.submit-btn {
  width: 100%; display: flex; align-items: center; justify-content: center;
  gap: 10px; padding: 13px 24px; border-radius: 6px; border: none;
  background: var(--accent); color: #FFFFFF;
  font-family: var(--fb); font-size: 14px; font-weight: 600;
  letter-spacing: .01em; cursor: pointer; text-decoration: none;
  transition: background 150ms, transform 80ms, opacity 150ms;
}

.submit-btn:hover:not(:disabled) { background: var(--accent-hi); }
.submit-btn:active:not(:disabled) { transform: scale(0.99); }
.submit-btn:disabled { opacity: .4; cursor: not-allowed; }
.submit-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.submit-btn--link { margin-top: 8px; display: flex; }

/* success state */
.success-body { display: flex; flex-direction: column; }

.success-icon-wrap {
  width: 52px; height: 52px; border-radius: 10px;
  background: rgba(22,163,74,.08); border: 1px solid rgba(22,163,74,.2);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px;
}

.success-icon { width: 26px; height: 26px; color: var(--green); }

.email-highlight { color: var(--accent); font-weight: 500; font-style: normal; }

.notice {
  font-size: 11px; font-family: var(--fm); color: var(--t3);
  letter-spacing: .04em; line-height: 1.6;
  padding: 10px 12px; border-radius: 6px;
  border: 1px solid var(--border); background: var(--bg);
  margin: 12px 0 20px;
}

.icon-sm { width: 16px; height: 16px; }
.spinner { animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
