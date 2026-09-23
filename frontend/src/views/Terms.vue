<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()
const { theme, apply: applyTheme } = useTheme()

function toggleTheme() {
  applyTheme(theme.value === 'dark' ? 'light' : 'dark')
}

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

<template>
  <div class="min-h-screen bg-slate-100 dark:bg-gray-950 py-10 px-4">

    <!-- Boton tema -->
    <button @click="toggleTheme"
      class="fixed top-4 right-4 z-50 p-2 rounded-lg bg-white/80 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white shadow transition"
      :title="theme === 'dark' ? 'Modo claro' : 'Modo oscuro'">
      <svg v-if="theme === 'dark'" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
      </svg>
    </button>

    <div class="max-w-3xl mx-auto">

      <!-- Encabezado -->
      <div class="flex items-center gap-4 mb-8">
        <img src="/logo-sgic.png" alt="Coyuntura SGIC" class="w-14 h-14 object-contain flex-shrink-0" />
        <div>
          <h1 class="text-2xl font-black text-gray-900 dark:text-white">Coyuntura SGIC</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">Para continuar debe leer y aceptar los términos y condiciones de uso.</p>
        </div>
      </div>

      <!-- Documento -->
      <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-sm overflow-hidden mb-6">

        <!-- Titulo del documento -->
        <div class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-8 py-5">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">Términos y Condiciones de Uso</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Coyuntura SGIC — Sistema de Monitoreo de Eventos Viales</p>
        </div>

        <!-- Contenido scrolleable -->
        <div class="px-8 py-6 max-h-[520px] overflow-y-auto text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-6 scroll-smooth">
          <section v-for="(art, i) in articles" :key="i">
            <h3 class="font-bold text-gray-900 dark:text-white mb-2">{{ art.title }}</h3>
            <p>{{ art.body }}</p>
          </section>
        </div>
      </div>

      <!-- Confirmacion y boton -->
      <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl px-8 py-6 shadow-sm">

        <label class="flex items-start gap-3 cursor-pointer mb-6">
          <div class="relative mt-0.5 flex-shrink-0">
            <input type="checkbox" v-model="accepted" class="sr-only peer" />
            <div class="w-5 h-5 rounded border-2 border-gray-300 dark:border-gray-600 peer-checked:bg-red-600 peer-checked:border-red-600 transition-colors flex items-center justify-center">
              <svg v-if="accepted" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
          </div>
          <span class="text-sm text-gray-700 dark:text-gray-300 leading-snug">
            He leído, comprendido y acepto en su totalidad los Términos y Condiciones de Uso del sistema Coyuntura SGIC.
            Entiendo que esta aceptación queda registrada con fecha y hora como constancia formal.
          </span>
        </label>

        <div class="flex items-center justify-between gap-3 flex-wrap">
          <p class="text-xs text-gray-400 dark:text-gray-500">
            Debe marcar la casilla para continuar.
          </p>
          <button
            type="button"
            @click="accept"
            :disabled="!accepted || loading"
            class="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition shadow-lg
                   disabled:opacity-40 disabled:cursor-not-allowed
                   bg-red-600 hover:bg-red-500 disabled:hover:bg-red-600
                   text-white shadow-red-900/30">
            <svg v-if="loading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {{ loading ? 'Procesando...' : 'Acepto los términos y condiciones' }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>
