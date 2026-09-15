<template>
  <div class="min-h-screen" style="background:var(--bg)">
    <!-- Header -->
    <header class="border-b sticky top-0 z-20" style="background:var(--surface);border-color:var(--border)">
      <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <router-link to="/dashboard" class="transition-colors" style="color:var(--t2)">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
            </svg>
          </router-link>
          <span class="font-display font-semibold" style="color:var(--t1)">Gestión de Usuarios</span>
          <span class="font-mono text-xs px-2 py-0.5 rounded-full border" style="color:var(--t2);background:var(--bg);border-color:var(--border)">
            {{ users.length }} usuarios
          </span>
        </div>
        <button @click="showForm = !showForm"
          class="flex items-center gap-2 px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors"
          style="background:var(--accent)" @mouseover="$event.currentTarget.style.background='var(--accent-hi)'" @mouseleave="$event.currentTarget.style.background='var(--accent)'">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Nuevo usuario
        </button>
      </div>
    </header>

    <div class="max-w-4xl mx-auto px-6 py-8 space-y-6">

      <!-- Create form -->
      <div v-if="showForm" class="rounded-xl p-6 border" style="background:var(--surface);border-color:var(--border)">
        <h2 class="font-display font-semibold mb-5" style="color:var(--t1)">Crear nuevo usuario</h2>
        <form @submit.prevent="createUser" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Nombre *</label>
              <input v-model="newUser.name" type="text" required
                class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
                style="background:var(--bg);border-color:var(--border);color:var(--t1)"
                @focus="$event.target.style.borderColor='var(--accent)'" @blur="$event.target.style.borderColor='var(--border)'" />
              <p v-if="errors.name" class="text-xs mt-1" style="color:#DC2626">{{ errors.name }}</p>
            </div>
            <div>
              <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Correo *</label>
              <input v-model="newUser.email" type="email" required
                class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
                style="background:var(--bg);border-color:var(--border);color:var(--t1)"
                @focus="$event.target.style.borderColor='var(--accent)'" @blur="$event.target.style.borderColor='var(--border)'" />
              <p v-if="errors.email" class="text-xs mt-1" style="color:#DC2626">{{ errors.email }}</p>
            </div>
          </div>

          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Contraseña *</label>
            <input v-model="newUser.password" type="password" required minlength="8"
              class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              placeholder="Mínimo 8 caracteres"
              @focus="$event.target.style.borderColor='var(--accent)'" @blur="$event.target.style.borderColor='var(--border)'" />
            <p v-if="errors.password" class="text-xs mt-1" style="color:#DC2626">{{ errors.password }}</p>
          </div>

          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Rol *</label>
            <div class="flex gap-2">
              <button type="button" @click="newUser.role = 'lector'"
                class="flex-1 py-2 rounded-lg border text-sm font-medium transition-colors"
                :style="newUser.role === 'lector'
                  ? 'background:var(--bg);border-color:var(--t1);color:var(--t1)'
                  : 'background:transparent;border-color:var(--border);color:var(--t2)'">
                Lector
              </button>
              <button type="button" @click="newUser.role = 'editor'"
                class="flex-1 py-2 rounded-lg border text-sm font-medium transition-colors"
                :style="newUser.role === 'editor'
                  ? 'background:var(--accent);border-color:var(--accent);color:#fff'
                  : 'background:transparent;border-color:var(--border);color:var(--t2)'">
                Editor
              </button>
            </div>
          </div>

          <div v-if="createError" class="text-xs px-3 py-2 rounded-lg" style="background:#FEF2F2;border:1px solid #FECACA;color:#DC2626">
            {{ createError }}
          </div>

          <div class="flex gap-3">
            <button type="button" @click="showForm = false"
              class="px-5 py-2 text-sm rounded-lg border transition-colors"
              style="background:var(--bg);border-color:var(--border);color:var(--t2)">
              Cancelar
            </button>
            <button type="submit" :disabled="createLoading"
              class="px-5 py-2 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
              style="background:var(--accent)">
              <svg v-if="createLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ createLoading ? 'Creando...' : 'Crear usuario' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Users table -->
      <div class="rounded-xl overflow-hidden border" style="background:var(--surface);border-color:var(--border)">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b" style="background:var(--bg);border-color:var(--border)">
                <th class="text-left px-5 py-3 font-mono text-xs uppercase tracking-wide" style="color:var(--t2)">Usuario</th>
                <th class="text-left px-5 py-3 font-mono text-xs uppercase tracking-wide" style="color:var(--t2)">Correo</th>
                <th class="text-left px-5 py-3 font-mono text-xs uppercase tracking-wide" style="color:var(--t2)">Rol</th>
                <th class="text-left px-5 py-3 font-mono text-xs uppercase tracking-wide" style="color:var(--t2)">Registrado</th>
                <th class="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id"
                class="border-b transition-colors"
                style="border-color:var(--border)"
                @mouseover="$event.currentTarget.style.background='var(--bg)'"
                @mouseleave="$event.currentTarget.style.background='transparent'">
                <td class="px-5 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold shrink-0" style="background:var(--accent)">
                      {{ u.name?.[0]?.toUpperCase() }}
                    </div>
                    <span class="text-sm font-medium" style="color:var(--t1)">{{ u.name }}</span>
                  </div>
                </td>
                <td class="px-5 py-4 text-sm" style="color:var(--t2)">{{ u.email }}</td>
                <td class="px-5 py-4">
                  <select v-if="u.id !== auth.user?.id"
                    :value="u.role" @change="updateRole(u, $event.target.value)"
                    class="px-2 py-1 rounded-lg text-xs outline-none border transition-colors"
                    :style="u.role === 'editor'
                      ? 'color:var(--accent);background:var(--accent-dim);border-color:var(--accent)'
                      : 'color:var(--t2);background:var(--bg);border-color:var(--border)'">
                    <option value="lector">Lector</option>
                    <option value="editor">Editor</option>
                  </select>
                  <span v-else class="px-2.5 py-1 rounded-full text-xs font-medium border"
                    :style="u.role === 'editor'
                      ? 'color:var(--accent);background:var(--accent-dim);border-color:var(--accent)'
                      : 'color:var(--t2);background:var(--bg);border-color:var(--border)'">
                    {{ u.role === 'editor' ? 'Editor' : 'Lector' }}
                  </span>
                </td>
                <td class="px-5 py-4 font-mono text-xs" style="color:var(--t3)">
                  {{ new Date(u.created_at).toLocaleDateString('es-GT') }}
                </td>
                <td class="px-5 py-4 text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button @click="resetPasswordUser = u; newPassword = ''; resetError = ''"
                      class="p-1.5 rounded-lg transition-colors"
                      style="color:var(--t2)"
                      title="Restablecer contraseña"
                      @mouseover="$event.currentTarget.style.background='var(--bg)'"
                      @mouseleave="$event.currentTarget.style.background='transparent'">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z"/>
                      </svg>
                    </button>
                    <button v-if="u.id !== auth.user?.id" @click="confirmDeleteUser = u"
                      class="p-1.5 rounded-lg transition-colors"
                      style="color:#DC2626"
                      title="Eliminar usuario"
                      @mouseover="$event.currentTarget.style.background='#FEF2F2'"
                      @mouseleave="$event.currentTarget.style.background='transparent'">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
                      </svg>
                    </button>
                    <span v-else class="font-mono text-xs" style="color:var(--t3)">Tú</span>
                  </div>
                </td>
              </tr>
              <tr v-if="users.length === 0">
                <td colspan="5" class="px-5 py-10 text-center text-sm" style="color:var(--t2)">Sin usuarios</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Reset password modal -->
    <div v-if="resetPasswordUser" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="resetPasswordUser = null"></div>
      <div class="relative rounded-xl p-6 max-w-sm w-full border shadow-xl" style="background:var(--surface);border-color:var(--border)">
        <h3 class="font-display font-semibold mb-2" style="color:var(--t1)">Restablecer contraseña</h3>
        <p class="text-sm mb-4" style="color:var(--t2)">
          Nueva contraseña para <span class="font-medium" style="color:var(--t1)">{{ resetPasswordUser.name }}</span>
        </p>
        <form @submit.prevent="doResetPassword" class="space-y-4">
          <div>
            <input v-model="newPassword" type="password" required minlength="8" autofocus
              class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              placeholder="Mínimo 8 caracteres"
              @focus="$event.target.style.borderColor='var(--accent)'" @blur="$event.target.style.borderColor='var(--border)'" />
            <p v-if="resetError" class="text-xs mt-1" style="color:#DC2626">{{ resetError }}</p>
          </div>
          <div class="flex gap-3">
            <button type="button" @click="resetPasswordUser = null"
              class="flex-1 py-2 text-sm rounded-lg border transition-colors"
              style="background:var(--bg);border-color:var(--border);color:var(--t2)">
              Cancelar
            </button>
            <button type="submit" :disabled="resetLoading"
              class="flex-1 py-2 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
              style="background:var(--accent)">
              {{ resetLoading ? 'Guardando...' : 'Restablecer' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <div v-if="confirmDeleteUser" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="confirmDeleteUser = null"></div>
      <div class="relative rounded-xl p-6 max-w-sm w-full border shadow-xl" style="background:var(--surface);border-color:var(--border)">
        <h3 class="font-display font-semibold mb-2" style="color:var(--t1)">¿Eliminar usuario?</h3>
        <p class="text-sm mb-1" style="color:var(--t2)">Se eliminará la cuenta de:</p>
        <p class="font-medium mb-5" style="color:var(--t1)">{{ confirmDeleteUser.name }} <span style="color:var(--t2)">({{ confirmDeleteUser.email }})</span></p>
        <div class="flex gap-3">
          <button @click="confirmDeleteUser = null"
            class="flex-1 py-2 text-sm rounded-lg border transition-colors"
            style="background:var(--bg);border-color:var(--border);color:var(--t2)">
            Cancelar
          </button>
          <button @click="doDeleteUser"
            class="flex-1 py-2 text-white text-sm rounded-lg transition-colors"
            style="background:#DC2626">
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const users = ref([])
const showForm = ref(false)
const confirmDeleteUser = ref(null)
const createLoading = ref(false)
const createError = ref('')
const errors = ref({})

const resetPasswordUser = ref(null)
const newPassword = ref('')
const resetError = ref('')
const resetLoading = ref(false)

const newUser = ref({ name: '', email: '', password: '', role: 'lector' })

async function fetchUsers() {
  try {
    const { data } = await api.get('/api/usuarios')
    users.value = data
  } catch {}
}

async function createUser() {
  errors.value = {}
  createError.value = ''
  createLoading.value = true
  try {
    const fd = new FormData()
    fd.append('name', newUser.value.name)
    fd.append('email', newUser.value.email)
    fd.append('password', newUser.value.password)
    fd.append('role', newUser.value.role)
    const { data } = await api.post('/api/usuarios', fd)
    users.value.unshift(data)
    newUser.value = { name: '', email: '', password: '', role: 'lector' }
    showForm.value = false
  } catch (e) {
    createError.value = e.response?.data?.detail || 'Error al crear usuario'
  } finally {
    createLoading.value = false
  }
}

async function updateRole(u, role) {
  const fd = new FormData()
  fd.append('role', role)
  try {
    await api.patch(`/api/usuarios/${u.id}/role`, fd)
    u.role = role
  } catch {}
}

async function doResetPassword() {
  if (!resetPasswordUser.value) return
  resetError.value = ''
  resetLoading.value = true
  try {
    const fd = new FormData()
    fd.append('new_password', newPassword.value)
    await api.patch(`/api/usuarios/${resetPasswordUser.value.id}/password`, fd)
    resetPasswordUser.value = null
    newPassword.value = ''
  } catch (e) {
    resetError.value = e.response?.data?.detail || 'Error al restablecer la contraseña'
  } finally {
    resetLoading.value = false
  }
}

async function doDeleteUser() {
  if (!confirmDeleteUser.value) return
  try {
    await api.delete(`/api/usuarios/${confirmDeleteUser.value.id}`)
    users.value = users.value.filter((u) => u.id !== confirmDeleteUser.value.id)
  } catch {}
  confirmDeleteUser.value = null
}

onMounted(fetchUsers)
</script>
