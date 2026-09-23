<script setup>
import { ref } from 'vue'

const form = ref({ email: '' })
const loading = ref(false)
const sent = ref(false)

async function submit() {
  loading.value = true
  await new Promise((r) => setTimeout(r, 800))
  sent.value = true
  loading.value = false
}
</script>

<template>
  <div class="min-h-screen bg-slate-100 dark:bg-gray-950 flex items-center justify-center p-6 relative">

    <!-- Back link -->
    <router-link to="/login"
      class="absolute top-6 left-6 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
      </svg>
      Volver al inicio de sesión
    </router-link>

    <div class="w-full max-w-md">

      <!-- Encabezado de marca -->
      <div class="flex flex-col items-center gap-3 mb-6 text-center">
        <img src="/logo-sgic.png" alt="Coyuntura SGIC" class="w-14 h-14 object-contain" />
        <h1 class="text-2xl font-black text-gray-900 dark:text-white leading-none">Coyuntura SGIC</h1>
      </div>

      <!-- Card -->
      <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-sm p-8">

        <!-- Success state -->
        <div v-if="sent" class="text-center">
          <div class="w-14 h-14 mx-auto rounded-2xl bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <p class="text-xs font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-400 mb-1.5">Solicitud enviada</p>
          <h2 class="text-xl font-black text-gray-900 dark:text-white mb-2">Revisa tu correo</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Enviamos instrucciones de recuperación a
            <strong class="text-gray-700 dark:text-gray-200 font-semibold">{{ form.email }}</strong>
          </p>
          <p class="text-xs font-mono text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 mt-4 mb-5">
            Si no recibes el correo, contacta al administrador del sistema.
          </p>
          <router-link to="/login"
            class="block w-full py-2.5 bg-red-600 hover:bg-red-500 text-white text-sm font-bold rounded-xl transition-colors">
            Volver al inicio de sesión
          </router-link>
        </div>

        <!-- Form state -->
        <template v-else>
          <div class="mb-6">
            <p class="text-xs font-bold uppercase tracking-widest text-red-500 dark:text-red-400 mb-1.5">Recuperación de acceso</p>
            <h2 class="text-2xl font-black text-gray-900 dark:text-white">Recuperar contraseña</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Ingresa tu correo y te enviaremos instrucciones para recuperar el acceso.</p>
          </div>

          <form @submit.prevent="submit" class="space-y-4" novalidate>
            <div>
              <label for="fp-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Correo electrónico</label>
              <div class="relative">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"/>
                </svg>
                <input id="fp-email" v-model="form.email" type="email" required autocomplete="email"
                  placeholder="correo@ejemplo.com"
                  class="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 rounded-xl pl-10 pr-3 py-2.5 text-sm transition-colors focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500" />
              </div>
            </div>

            <button type="submit" :disabled="loading"
              class="w-full flex items-center justify-center gap-2 py-2.5 bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold rounded-xl transition-colors">
              <svg v-if="loading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              <span>{{ loading ? 'Enviando...' : 'Enviar instrucciones' }}</span>
              <svg v-if="!loading" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12h15m0 0l-6.75-6.75M19.5 12l-6.75 6.75"/>
              </svg>
            </button>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>
