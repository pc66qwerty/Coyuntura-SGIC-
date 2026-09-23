<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const users = ref([])
const showCreate = ref(false)
const updating = ref(null)
const deleting = ref(null)
const confirmDeleteUser = ref(null)
const createLoading = ref(false)
const createError = ref('')

const resetPasswordUser = ref(null)
const newPassword = ref('')
const resetError = ref('')
const resetLoading = ref(false)

const editEmailUser = ref(null)
const newEmail = ref('')
const emailError = ref('')
const emailLoading = ref(false)

const form = ref({ name: '', email: '', password: '', role: 'lector' })

async function fetchUsers() {
  try {
    const { data } = await api.get('/api/usuarios')
    users.value = data
  } catch {}
}

async function createUser() {
  createError.value = ''
  createLoading.value = true
  try {
    const fd = new FormData()
    fd.append('name', form.value.name)
    fd.append('email', form.value.email)
    fd.append('password', form.value.password)
    fd.append('role', form.value.role)
    const { data } = await api.post('/api/usuarios', fd)
    users.value.unshift(data)
    form.value = { name: '', email: '', password: '', role: 'lector' }
    showCreate.value = false
  } catch (e) {
    createError.value = e.response?.data?.detail || 'Error al crear usuario'
  } finally {
    createLoading.value = false
  }
}

async function setRole(u, role) {
  if (u.role === role) return
  updating.value = u.id
  const fd = new FormData()
  fd.append('role', role)
  try {
    await api.patch(`/api/usuarios/${u.id}/role`, fd)
    u.role = role
  } catch {} finally {
    updating.value = null
  }
}

async function doUpdateEmail() {
  if (!editEmailUser.value) return
  emailError.value = ''
  emailLoading.value = true
  try {
    const fd = new FormData()
    fd.append('email', newEmail.value)
    await api.patch(`/api/usuarios/${editEmailUser.value.id}/email`, fd)
    editEmailUser.value.email = newEmail.value
    editEmailUser.value = null
  } catch (e) {
    emailError.value = e.response?.data?.detail || 'Error al actualizar el correo'
  } finally {
    emailLoading.value = false
  }
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
  deleting.value = confirmDeleteUser.value.id
  try {
    await api.delete(`/api/usuarios/${confirmDeleteUser.value.id}`)
    users.value = users.value.filter((u) => u.id !== confirmDeleteUser.value.id)
  } catch {} finally {
    deleting.value = null
    confirmDeleteUser.value = null
  }
}

onMounted(fetchUsers)
</script>

<template>
  <div class="min-h-screen bg-[#EEF2FA] dark:bg-[#131314] px-4 sm:px-6 lg:px-8 py-6">
    <div class="max-w-3xl mx-auto space-y-4">

      <!-- Header -->
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="flex items-center gap-2">
            <router-link to="/dashboard" class="text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
              </svg>
            </router-link>
            <h1 class="text-lg font-semibold text-gray-900 dark:text-white">Usuarios</h1>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            {{ users.length }} cuenta{{ users.length !== 1 ? 's' : '' }} registrada{{ users.length !== 1 ? 's' : '' }}
          </p>
        </div>
        <button
          @click="showCreate = !showCreate"
          class="flex items-center gap-1.5 px-3 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-semibold rounded-xl transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 flex-shrink-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo usuario
        </button>
      </div>

      <!-- Formulario crear usuario -->
      <transition
        enter-active-class="transition-[opacity,transform] duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-[opacity,transform] duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-1"
      >
        <div v-if="showCreate" class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-5">
          <h2 class="text-sm font-semibold text-gray-900 dark:text-white mb-4">Nueva cuenta</h2>
          <form @submit.prevent="createUser" class="space-y-3" novalidate>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">

              <div>
                <label for="new-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre completo</label>
                <input
                  id="new-name"
                  v-model="form.name"
                  type="text"
                  name="name"
                  required
                  autocomplete="name"
                  placeholder="Ej. Juan Pérez"
                  class="w-full bg-white dark:bg-[#131314] border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 rounded-xl px-3 py-2.5 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                />
              </div>

              <div>
                <label for="new-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Correo electrónico</label>
                <input
                  id="new-email"
                  v-model="form.email"
                  type="email"
                  name="email"
                  required
                  autocomplete="email"
                  spellcheck="false"
                  placeholder="correo@ejemplo.com"
                  class="w-full bg-white dark:bg-[#131314] border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 rounded-xl px-3 py-2.5 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                />
              </div>

              <div>
                <label for="new-password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contraseña</label>
                <input
                  id="new-password"
                  v-model="form.password"
                  type="password"
                  name="password"
                  required
                  minlength="8"
                  autocomplete="new-password"
                  placeholder="Mínimo 8 caracteres"
                  class="w-full bg-white dark:bg-[#131314] border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 rounded-xl px-3 py-2.5 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rol</label>
                <div class="flex gap-2">
                  <button
                    type="button"
                    @click="form.role = 'lector'"
                    class="flex-1 py-2.5 rounded-xl text-sm font-medium border transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                    :class="form.role === 'lector'
                      ? 'bg-[#E8EDF5] dark:bg-[#2A2A2A] border-gray-300 dark:border-gray-500 text-gray-900 dark:text-white'
                      : 'bg-white dark:bg-transparent border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-400 dark:text-gray-500 hover:border-gray-400 dark:hover:border-gray-400'"
                  >
                    Lector
                  </button>
                  <button
                    type="button"
                    @click="form.role = 'editor'"
                    class="flex-1 py-2.5 rounded-xl text-sm font-medium border transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                    :class="form.role === 'editor'
                      ? 'bg-indigo-600 border-indigo-600 text-white'
                      : 'bg-white dark:bg-transparent border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-400 dark:text-gray-500 hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-600 dark:hover:text-indigo-400'"
                  >
                    Editor
                  </button>
                </div>
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-1.5">
                  Los editores pueden crear y modificar eventos.
                </p>
              </div>
            </div>

            <p v-if="createError" class="text-red-600 dark:text-red-400 text-xs">{{ createError }}</p>

            <div class="flex items-center justify-end gap-2 pt-1 border-t border-[#E2E8F0] dark:border-[#2A2A2A] mt-1">
              <button
                type="button"
                @click="showCreate = false"
                class="px-4 py-2 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors focus:outline-none focus-visible:underline"
              >
                Cancelar
              </button>
              <button
                type="submit"
                :disabled="createLoading"
                class="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2"
              >
                <svg v-if="createLoading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
                {{ createLoading ? 'Creando…' : 'Crear cuenta' }}
              </button>
            </div>
          </form>
        </div>
      </transition>

      <!-- Lista de usuarios -->
      <div class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl overflow-hidden">

        <div v-if="users.length === 0" class="py-16 text-center">
          <p class="text-sm text-gray-400 dark:text-gray-500">No hay usuarios registrados.</p>
        </div>

        <div v-else class="divide-y divide-[#E2E8F0] dark:divide-[#2A2A2A]">
          <div
            v-for="u in users"
            :key="u.id"
            class="flex items-center justify-between px-5 py-3.5 hover:bg-[#F5F7FC] dark:hover:bg-[#242424] transition-colors gap-3"
          >
            <!-- Avatar + info -->
            <div class="flex items-center gap-3 min-w-0">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white flex-shrink-0 select-none"
                :class="u.role === 'editor' ? 'bg-indigo-600' : 'bg-gray-400 dark:bg-gray-600'"
                aria-hidden="true"
              >
                {{ u.name.charAt(0).toUpperCase() }}
              </div>
              <div class="min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ u.name }}</p>
                  <span
                    class="px-1.5 py-0.5 rounded-md text-xs font-medium border flex-shrink-0"
                    :class="u.role === 'editor'
                      ? 'bg-indigo-50 text-indigo-600 border-indigo-200 dark:bg-indigo-900/30 dark:text-indigo-300 dark:border-indigo-800'
                      : 'bg-[#EEF2FA] text-gray-500 border-[#E2E8F0] dark:bg-[#252525] dark:text-gray-400 dark:border-[#2A2A2A]'"
                  >
                    {{ u.role }}
                  </span>
                  <span v-if="u.id === auth.user?.id" class="text-xs text-gray-400 dark:text-gray-500">(tú)</span>
                </div>
                <p class="text-xs text-gray-400 dark:text-gray-500 truncate">{{ u.email }}</p>
              </div>
            </div>

            <!-- Acciones -->
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <div v-if="updating === u.id || deleting === u.id" class="flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500 px-2">
                <svg class="animate-spin h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
                <span class="hidden sm:inline">Guardando…</span>
              </div>

              <template v-else>
                <button
                  v-if="u.id !== auth.user?.id"
                  @click="setRole(u, 'lector')"
                  class="px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
                  :class="u.role === 'lector'
                    ? 'bg-[#E8EDF5] dark:bg-[#2A2A2A] border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200'
                    : 'bg-white dark:bg-transparent border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-400 dark:text-gray-500 hover:border-gray-400 hover:text-gray-700 dark:hover:border-gray-500 dark:hover:text-gray-300'"
                >
                  Lector
                </button>
                <button
                  v-if="u.id !== auth.user?.id"
                  @click="setRole(u, 'editor')"
                  class="px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                  :class="u.role === 'editor'
                    ? 'bg-indigo-600 border-indigo-600 text-white'
                    : 'bg-white dark:bg-transparent border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-400 dark:text-gray-500 hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-600 dark:hover:text-indigo-400'"
                >
                  Editor
                </button>
                <button
                  @click="editEmailUser = u; newEmail = u.email; emailError = ''"
                  :aria-label="`Cambiar correo de ${u.name}`"
                  title="Cambiar correo"
                  class="p-1.5 rounded-lg text-gray-300 dark:text-gray-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 hover:text-indigo-500 dark:hover:text-indigo-400 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"/>
                  </svg>
                </button>
                <button
                  @click="resetPasswordUser = u; newPassword = ''; resetError = ''"
                  :aria-label="`Restablecer contraseña de ${u.name}`"
                  title="Restablecer contraseña"
                  class="p-1.5 rounded-lg text-gray-300 dark:text-gray-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 hover:text-indigo-500 dark:hover:text-indigo-400 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z"/>
                  </svg>
                </button>
                <button
                  v-if="u.id !== auth.user?.id"
                  @click="confirmDeleteUser = u"
                  :aria-label="`Eliminar a ${u.name}`"
                  title="Eliminar usuario"
                  class="p-1.5 rounded-lg text-gray-300 dark:text-gray-600 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500 dark:hover:text-red-400 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <p class="text-xs text-gray-400 dark:text-gray-600 text-center">
        Los cambios de rol aplican en el siguiente inicio de sesión del usuario.
      </p>

    </div>

    <!-- Editar correo modal -->
    <div v-if="editEmailUser" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="editEmailUser = null"></div>
      <div class="relative bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-6 max-w-sm w-full shadow-xl">
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Cambiar correo</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Nuevo correo para <span class="font-medium text-gray-900 dark:text-white">{{ editEmailUser.name }}</span>
        </p>
        <form @submit.prevent="doUpdateEmail" class="space-y-4">
          <div>
            <input v-model="newEmail" type="email" required autofocus
              placeholder="correo@ejemplo.com"
              class="w-full bg-white dark:bg-[#131314] border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 rounded-xl px-3 py-2.5 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500" />
            <p v-if="emailError" class="text-red-600 dark:text-red-400 text-xs mt-1">{{ emailError }}</p>
          </div>
          <div class="flex gap-3">
            <button type="button" @click="editEmailUser = null"
              class="flex-1 py-2 text-sm font-medium rounded-xl border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
              Cancelar
            </button>
            <button type="submit" :disabled="emailLoading"
              class="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-colors">
              {{ emailLoading ? 'Guardando…' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Reset password modal -->
    <div v-if="resetPasswordUser" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="resetPasswordUser = null"></div>
      <div class="relative bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-6 max-w-sm w-full shadow-xl">
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Restablecer contraseña</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Nueva contraseña para <span class="font-medium text-gray-900 dark:text-white">{{ resetPasswordUser.name }}</span>
        </p>
        <form @submit.prevent="doResetPassword" class="space-y-4">
          <div>
            <input v-model="newPassword" type="password" required minlength="8" autofocus
              placeholder="Mínimo 8 caracteres"
              class="w-full bg-white dark:bg-[#131314] border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 rounded-xl px-3 py-2.5 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500" />
            <p v-if="resetError" class="text-red-600 dark:text-red-400 text-xs mt-1">{{ resetError }}</p>
          </div>
          <div class="flex gap-3">
            <button type="button" @click="resetPasswordUser = null"
              class="flex-1 py-2 text-sm font-medium rounded-xl border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
              Cancelar
            </button>
            <button type="submit" :disabled="resetLoading"
              class="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-colors">
              {{ resetLoading ? 'Guardando…' : 'Restablecer' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <div v-if="confirmDeleteUser" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="confirmDeleteUser = null"></div>
      <div class="relative bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-6 max-w-sm w-full shadow-xl">
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">¿Eliminar usuario?</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Se eliminará la cuenta de:</p>
        <p class="font-medium text-gray-900 dark:text-white mb-5">{{ confirmDeleteUser.name }} <span class="text-gray-500 dark:text-gray-400 font-normal">({{ confirmDeleteUser.email }})</span></p>
        <div class="flex gap-3">
          <button @click="confirmDeleteUser = null"
            class="flex-1 py-2 text-sm font-medium rounded-xl border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
            Cancelar
          </button>
          <button @click="doDeleteUser"
            class="flex-1 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-semibold rounded-xl transition-colors">
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
