<template>
  <div class="min-h-screen flex flex-col" style="background:var(--bg)">
    <!-- Header -->
    <header class="shrink-0 border-b" style="background:var(--surface);border-color:var(--border)">
      <div class="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background:var(--accent)">
            <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c-.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"/>
            </svg>
          </div>
          <span class="font-display font-semibold text-sm" style="color:var(--t1)">Monitor Vial</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="font-mono text-xs px-3 py-1 rounded-full border" style="color:var(--warning);background:rgba(217,119,6,.08);border-color:rgba(217,119,6,.25)">
            Acepta para continuar
          </span>
          <div class="theme-switch" aria-label="Tema visual">
            <button type="button" :class="{ active: theme === 'light' }" @click="applyTheme('light')">Claro</button>
            <button type="button" :class="{ active: theme === 'dark' }" @click="applyTheme('dark')">Oscuro</button>
          </div>
        </div>
      </div>
    </header>

    <!-- Content -->
    <div class="flex-1 max-w-3xl mx-auto w-full px-6 py-10 overflow-y-auto">
      <h1 class="font-display text-3xl font-bold mb-1" style="color:var(--t1)">Términos y Condiciones de Uso</h1>
      <p class="font-mono text-xs mb-10" style="color:var(--t2)">Monitor Vial — Sistema de Monitoreo de Eventos Viales</p>

      <div class="space-y-8 text-sm leading-relaxed" style="color:var(--t2)">
        <section v-for="(art, i) in articles" :key="i">
          <h2 class="font-display font-semibold text-base mb-2" style="color:var(--t1)">{{ art.title }}</h2>
          <p>{{ art.body }}</p>
        </section>
      </div>

      <!-- Acceptance -->
      <div class="mt-12 pt-8 border-t" style="border-color:var(--border)">
        <label class="flex items-start gap-3 cursor-pointer mb-5">
          <input v-model="accepted" type="checkbox" class="mt-0.5 w-4 h-4 rounded" style="accent-color:var(--accent)" />
          <span class="text-sm" style="color:var(--t1)">
            He leído, comprendido y acepto los Términos y Condiciones de uso del sistema Monitor Vial.
          </span>
        </label>

        <button @click="accept" :disabled="!accepted || loading"
          class="w-full py-3 text-white font-medium rounded-xl text-sm flex items-center justify-center gap-2 transition-colors"
          :style="{ background: (!accepted || loading) ? 'var(--t3)' : 'var(--accent)', cursor: (!accepted || loading) ? 'not-allowed' : 'pointer' }">
          <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          {{ loading ? 'Procesando...' : 'Aceptar y continuar' }}
        </button>
      </div>
    </div>
  </div>
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

const accepted = ref(false)
const loading = ref(false)

const articles = [
  { title: '1. Alcance y aplicación', body: 'El presente sistema es una herramienta oficial de monitoreo de eventos viales en Guatemala. Su uso está reservado exclusivamente para personal autorizado por la institución administradora. Al acceder y utilizar este sistema, el usuario acepta cumplir con todos los términos aquí establecidos.' },
  { title: '2. Acceso autorizado y confidencialidad', body: 'Las credenciales de acceso son personales e intransferibles. El usuario es responsable de mantener la confidencialidad de su contraseña. Queda prohibido compartir credenciales con terceros o permitir el acceso no autorizado al sistema.' },
  { title: '3. Responsabilidad sobre la información registrada', body: 'Los usuarios con rol Editor son responsables de la veracidad, exactitud y oportunidad de la información que registren en el sistema. La información falsa o incorrecta puede tener consecuencias operativas y legales. Toda acción queda registrada y asociada al usuario que la realizó.' },
  { title: '4. Manejo de datos personales', body: 'Los datos personales recopilados (nombre, correo electrónico) serán utilizados únicamente para la autenticación y auditoría dentro del sistema. No serán compartidos con terceros ni utilizados para fines distintos al monitoreo vial institucional.' },
  { title: '5. Propiedad intelectual', body: 'El sistema, su diseño, código fuente y contenido son propiedad de la institución administradora. Queda prohibida su reproducción, distribución o modificación sin autorización expresa por escrito.' },
  { title: '6. Disponibilidad y limitación de responsabilidad', body: 'La institución administradora no garantiza la disponibilidad continua del sistema. No será responsable por daños derivados de interrupciones, pérdida de datos o errores técnicos fuera de su control.' },
  { title: '7. Modificación de los términos', body: 'Estos términos pueden ser modificados en cualquier momento. Los usuarios serán notificados y deberán aceptar los términos actualizados para continuar usando el sistema.' },
  { title: '8. Aceptación y registro', body: 'Al marcar la casilla de aceptación, el usuario declara haber leído, comprendido y aceptado todos los términos y condiciones. Esta aceptación queda registrada con fecha y hora en el sistema.' },
]

async function accept() {
  loading.value = true
  try {
    const { data } = await api.post('/api/auth/accept-terms')
    auth.setAuth({ token: data.token, user: { ...auth.user, terms_accepted: true } })
    router.push(auth.isEditor ? '/dashboard' : '/')
  } catch {
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.theme-switch {
  display: inline-grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  min-height: 36px;
  padding: 4px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
}

.theme-switch button {
  min-width: 58px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--t2);
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.theme-switch button.active {
  background: var(--surface);
  color: var(--t1);
  box-shadow: inset 0 0 0 1px var(--border);
}

.theme-switch button:hover {
  color: var(--accent);
}
</style>
