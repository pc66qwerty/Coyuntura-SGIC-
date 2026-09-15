<template>
  <div class="min-h-screen" style="background:var(--bg)">
    <!-- Nav -->
    <nav class="border-b" style="background:var(--surface);border-color:var(--border)">
      <div class="max-w-xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <router-link to="/" class="transition-colors" style="color:var(--t2)" @mouseover="$event.target.style.color='var(--t1)'" @mouseleave="$event.target.style.color='var(--t2)'">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
            </svg>
          </router-link>
          <span class="font-display font-semibold" style="color:var(--t1)">Editar perfil</span>
        </div>
        <span class="font-mono text-xs px-2.5 py-1 rounded-full border"
          :style="auth.isEditor
            ? 'color:var(--accent);background:var(--accent-dim);border-color:var(--accent)'
            : 'color:var(--t2);background:var(--bg);border-color:var(--border)'">
          {{ auth.isEditor ? 'Editor' : 'Lector' }}
        </span>
      </div>
    </nav>

    <div class="max-w-xl mx-auto px-6 py-10 space-y-5">

      <!-- Info card -->
      <div class="rounded-xl p-6 border" style="background:var(--surface);border-color:var(--border)">
        <h2 class="font-display font-semibold mb-5" style="color:var(--t1)">Información personal</h2>
        <form @submit.prevent="updateInfo" class="space-y-4">
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Nombre</label>
            <input v-model="infoForm.name" type="text" required
              class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
              :style="nameFocused ? 'background:var(--bg);border-color:var(--accent);color:var(--t1)' : 'background:var(--bg);border-color:var(--border);color:var(--t1)'"
              @focus="nameFocused=true" @blur="nameFocused=false" />
          </div>
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Correo electrónico</label>
            <input v-model="infoForm.email" type="email" required
              class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
              :style="emailFocused ? 'background:var(--bg);border-color:var(--accent);color:var(--t1)' : 'background:var(--bg);border-color:var(--border);color:var(--t1)'"
              @focus="emailFocused=true" @blur="emailFocused=false" />
          </div>
          <div v-if="infoError" class="flex items-center gap-2 text-xs px-3 py-2 rounded-lg" style="background:#FEF2F2;border:1px solid #FECACA;color:#DC2626">{{ infoError }}</div>
          <div v-if="infoSuccess" class="flex items-center gap-2 text-xs px-3 py-2 rounded-lg" style="background:rgba(22,163,74,.08);border:1px solid rgba(22,163,74,.2);color:#16A34A">{{ infoSuccess }}</div>
          <button type="submit" :disabled="infoLoading"
            class="px-5 py-2 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
            style="background:var(--accent)" @mouseover="$event.target.style.background='var(--accent-hi)'" @mouseleave="$event.target.style.background='var(--accent)'">
            {{ infoLoading ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </form>
      </div>

      <!-- Password card -->
      <div class="rounded-xl p-6 border" style="background:var(--surface);border-color:var(--border)">
        <h2 class="font-display font-semibold mb-5" style="color:var(--t1)">Cambiar contraseña</h2>
        <form @submit.prevent="updatePassword" class="space-y-4">
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Nueva contraseña</label>
            <input v-model="passForm.password" type="password" required
              class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
              :style="pass1Focused ? 'background:var(--bg);border-color:var(--accent);color:var(--t1)' : 'background:var(--bg);border-color:var(--border);color:var(--t1)'"
              placeholder="Mínimo 8 caracteres"
              @focus="pass1Focused=true" @blur="pass1Focused=false" />
          </div>
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Confirmar nueva contraseña</label>
            <input v-model="passForm.confirm" type="password" required
              class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
              :style="pass2Focused ? 'background:var(--bg);border-color:var(--accent);color:var(--t1)' : 'background:var(--bg);border-color:var(--border);color:var(--t1)'"
              @focus="pass2Focused=true" @blur="pass2Focused=false" />
          </div>
          <div v-if="passError" class="text-xs px-3 py-2 rounded-lg" style="background:#FEF2F2;border:1px solid #FECACA;color:#DC2626">{{ passError }}</div>
          <div v-if="passSuccess" class="text-xs px-3 py-2 rounded-lg" style="background:rgba(22,163,74,.08);border:1px solid rgba(22,163,74,.2);color:#16A34A">{{ passSuccess }}</div>
          <button type="submit" :disabled="passLoading"
            class="px-5 py-2 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
            style="background:var(--accent)" @mouseover="$event.target.style.background='var(--accent-hi)'" @mouseleave="$event.target.style.background='var(--accent)'">
            {{ passLoading ? 'Cambiando...' : 'Cambiar contraseña' }}
          </button>
        </form>
      </div>

      <!-- Danger zone -->
      <div class="rounded-xl p-6 border" style="background:var(--surface);border-color:#FECACA">
        <h2 class="font-display font-semibold mb-2" style="color:#DC2626">Zona de peligro</h2>
        <p class="text-sm mb-4" style="color:var(--t2)">Esta acción eliminará tu cuenta permanentemente y no se puede deshacer.</p>
        <button v-if="!confirmDelete" @click="confirmDelete = true"
          class="px-5 py-2 text-sm font-medium rounded-lg border transition-colors"
          style="background:#FEF2F2;color:#DC2626;border-color:#FECACA">
          Eliminar mi cuenta
        </button>
        <div v-else class="flex items-center gap-3">
          <button @click="deleteAccount"
            class="px-5 py-2 text-white text-sm font-medium rounded-lg transition-colors"
            style="background:#DC2626">
            Sí, eliminar cuenta
          </button>
          <button @click="confirmDelete = false"
            class="px-5 py-2 text-sm rounded-lg transition-colors border"
            style="background:var(--bg);border-color:var(--border);color:var(--t2)">
            Cancelar
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()

const infoForm = ref({ name: auth.user?.name || '', email: auth.user?.email || '' })
const infoLoading = ref(false)
const infoError = ref('')
const infoSuccess = ref('')
const nameFocused = ref(false)
const emailFocused = ref(false)

const passForm = ref({ password: '', confirm: '' })
const passLoading = ref(false)
const passError = ref('')
const passSuccess = ref('')
const pass1Focused = ref(false)
const pass2Focused = ref(false)

const confirmDelete = ref(false)

async function updateInfo() {
  infoError.value = ''
  infoSuccess.value = ''
  infoLoading.value = true
  try {
    const fd = new FormData()
    fd.append('name', infoForm.value.name)
    fd.append('email', infoForm.value.email)
    const { data } = await api.patch('/api/auth/profile', fd)
    auth.setAuth(data)
    infoSuccess.value = 'Información actualizada correctamente'
  } catch (e) {
    infoError.value = e.response?.data?.detail || 'Error al actualizar'
  } finally {
    infoLoading.value = false
  }
}

async function updatePassword() {
  passError.value = ''
  passSuccess.value = ''
  if (passForm.value.password !== passForm.value.confirm) {
    passError.value = 'Las contraseñas no coinciden'
    return
  }
  passLoading.value = true
  try {
    const fd = new FormData()
    fd.append('password', passForm.value.password)
    const { data } = await api.patch('/api/auth/profile', fd)
    auth.setAuth(data)
    passForm.value = { password: '', confirm: '' }
    passSuccess.value = 'Contraseña actualizada correctamente'
  } catch (e) {
    passError.value = e.response?.data?.detail || 'Error al cambiar contraseña'
  } finally {
    passLoading.value = false
  }
}

async function deleteAccount() {
  try {
    await api.delete('/api/auth/profile')
    auth.logout()
    router.push('/login')
  } catch {
    confirmDelete.value = false
  }
}
</script>
