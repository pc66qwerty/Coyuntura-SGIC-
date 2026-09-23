<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const tipos = ref([])
const showForm = ref(false)
const editingTipo = ref(null)
const confirmDelete = ref(null)
const saveLoading = ref(false)
const formError = ref('')

const form = ref({ nombre: '', color: '#2563EB', icon_path: '' })

const colorPalette = [
  '#DC2626', '#EA580C', '#D97706', '#CA8A04',
  '#16A34A', '#0D9488', '#2563EB', '#7C3AED',
  '#DB2777', '#475569',
]

const iconOptions = [
  { id: 'pin', label: 'Ubicación', d: 'M15 10.5a3 3 0 11-6 0 3 3 0 016 0z M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z' },
  { id: 'bolt', label: 'Emergencia', d: 'M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z' },
  { id: 'car', label: 'Vehículo', d: 'M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12' },
  { id: 'block', label: 'Bloqueo', d: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' },
  { id: 'wrench', label: 'Trabajos', d: 'M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z' },
  { id: 'check', label: 'Libre/OK', d: 'M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  { id: 'warning', label: 'Advertencia', d: 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z' },
  { id: 'people', label: 'Personas/Grupo', d: 'M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z' },
  { id: 'flag', label: 'Marcha/Caminata', d: 'M3 3v1.5M3 21v-6m0 0l2.77-.693a9 9 0 016.208.682l.108.054a9 9 0 006.086.71l3.114-.732a48.524 48.524 0 01-.005-10.499l-3.11.732a9 9 0 01-6.085-.711l-.108-.054a9 9 0 00-6.208-.682L3 4.5M3 15V4.5' },
  { id: 'run', label: 'Maratón', d: 'M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z' },
  { id: 'megaphone', label: 'Manifestación', d: 'M10.34 15.84c-.688-.06-1.386-.09-2.09-.09H7.5a4.5 4.5 0 110-9h.75c.704 0 1.402-.03 2.09-.09m0 9.18c.253.962.584 1.892.985 2.783.247.55.06 1.21-.463 1.511l-.657.38c-.551.318-1.26.117-1.527-.461a20.845 20.845 0 01-1.44-4.282m3.102.069a18.03 18.03 0 01-.59-4.59c0-1.586.205-3.124.59-4.59m0 9.18a23.848 23.848 0 018.835 2.535M10.34 6.66a23.847 23.847 0 008.835-2.535m0 0A23.74 23.74 0 0018.795 3m.38 1.125a23.91 23.91 0 011.014 5.395m-1.014 8.855c-.118.38-.245.754-.38 1.125m.38-1.125a23.91 23.91 0 001.014-5.395m0-3.46c.495.413.811 1.035.811 1.73 0 .695-.316 1.317-.811 1.73m0-3.46a24.347 24.347 0 010 3.46' },
  { id: 'clock', label: 'Temporal', d: 'M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z' },
  { id: 'truck', label: 'Camión/Maquinaria', d: 'M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12' },
]

const BUILTIN = ['Emergencia', 'Accidente vial', 'Bloqueo', 'Asistencia vial', 'Trabajos', 'Libre']

function makeLight(hex) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const lr = Math.round(r * 0.12 + 248 * 0.88)
  const lg = Math.round(g * 0.12 + 248 * 0.88)
  const lb = Math.round(b * 0.12 + 248 * 0.88)
  return `#${lr.toString(16).padStart(2, '0')}${lg.toString(16).padStart(2, '0')}${lb.toString(16).padStart(2, '0')}`
}

function makeBorder(hex) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const br = Math.round(r * 0.35 + 210 * 0.65)
  const bg_ = Math.round(g * 0.35 + 210 * 0.65)
  const bb = Math.round(b * 0.35 + 210 * 0.65)
  return `#${br.toString(16).padStart(2, '0')}${bg_.toString(16).padStart(2, '0')}${bb.toString(16).padStart(2, '0')}`
}

// icon_path se guarda en la base de datos como marcado SVG completo
// (ej. '<path d="..."/>'), igual que usan el mapa y la leyenda pública.
// El selector de íconos trabaja internamente con el string "d" simple.
function iconMarkup(iconPath) {
  if (!iconPath) return ''
  return iconPath.includes('<path') ? iconPath : `<path stroke-linecap="round" stroke-linejoin="round" d="${iconPath}"/>`
}

function extractD(iconPath) {
  if (!iconPath) return ''
  const match = iconPath.match(/\sd="([^"]+)"/)
  return match ? match[1] : iconPath
}

async function fetchTipos() {
  try {
    const { data } = await api.get('/api/tipos-evento')
    tipos.value = data.map((t) => ({ ...t, builtin: BUILTIN.includes(t.nombre) }))
  } catch {}
}

function openCreate() {
  editingTipo.value = null
  form.value = { nombre: '', color: '#2563EB', icon_path: '' }
  formError.value = ''
  showForm.value = true
}

function openEdit(t) {
  editingTipo.value = t
  form.value = { nombre: t.nombre, color: t.color, icon_path: extractD(t.icon_path) }
  formError.value = ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingTipo.value = null
}

async function saveTipo() {
  formError.value = ''
  if (!form.value.nombre.trim()) { formError.value = 'El nombre es requerido'; return }
  saveLoading.value = true
  try {
    const fd = new FormData()
    fd.append('nombre', form.value.nombre.trim())
    fd.append('color', form.value.color)
    fd.append('color_light', makeLight(form.value.color))
    fd.append('color_border', makeBorder(form.value.color))
    fd.append('icon_path', iconMarkup(form.value.icon_path))

    if (editingTipo.value) {
      const { data } = await api.patch(`/api/tipos-evento/${editingTipo.value.id}`, fd)
      const idx = tipos.value.findIndex((t) => t.id === editingTipo.value.id)
      if (idx !== -1) tipos.value[idx] = { ...data, builtin: BUILTIN.includes(data.nombre) }
    } else {
      const { data } = await api.post('/api/tipos-evento', fd)
      tipos.value.push({ ...data, builtin: false })
    }
    tipos.value.sort((a, b) => a.nombre.localeCompare(b.nombre))
    closeForm()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Error al guardar el tipo'
  } finally {
    saveLoading.value = false
  }
}

async function doDelete() {
  if (!confirmDelete.value) return
  try {
    await api.delete(`/api/tipos-evento/${confirmDelete.value.id}`)
    tipos.value = tipos.value.filter((t) => t.id !== confirmDelete.value.id)
  } catch {}
  confirmDelete.value = null
}

onMounted(fetchTipos)
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
            <h1 class="text-lg font-semibold text-gray-900 dark:text-white">Tipos de evento</h1>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            {{ tipos.length }} tipo{{ tipos.length !== 1 ? 's' : '' }} registrado{{ tipos.length !== 1 ? 's' : '' }}
          </p>
        </div>
        <button
          @click="showForm ? closeForm() : openCreate()"
          class="flex items-center gap-1.5 px-3 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-semibold rounded-xl transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 flex-shrink-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo tipo
        </button>
      </div>

      <!-- Formulario crear/editar -->
      <transition
        enter-active-class="transition-[opacity,transform] duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-[opacity,transform] duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-1"
      >
        <div v-if="showForm" class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-5">
          <h2 class="text-sm font-semibold text-gray-900 dark:text-white mb-4">
            {{ editingTipo ? 'Editar tipo de evento' : 'Nuevo tipo de evento' }}
          </h2>
          <div class="space-y-5">
            <!-- Nombre -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre *</label>
              <input v-model="form.nombre" type="text" placeholder="Ej: Caminata, Maratón..."
                class="w-full bg-white dark:bg-[#131314] border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 rounded-xl px-3 py-2.5 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500" />
            </div>

            <!-- Color -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Color *</label>
              <div class="flex flex-wrap gap-2">
                <button v-for="c in colorPalette" :key="c" type="button"
                  @click="form.color = c"
                  class="w-8 h-8 rounded-full border-2 transition-all"
                  :class="form.color === c ? 'border-gray-900 dark:border-white' : 'border-transparent'"
                  :style="{ background: c }">
                </button>
                <label class="w-8 h-8 rounded-full border-2 border-[#E2E8F0] dark:border-[#2A2A2A] flex items-center justify-center cursor-pointer transition-all overflow-hidden"
                  :style="{ background: form.color }" title="Color personalizado">
                  <input type="color" v-model="form.color" class="opacity-0 absolute w-0 h-0" />
                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487z"/>
                  </svg>
                </label>
              </div>
              <p class="font-mono text-xs mt-1.5 text-gray-400 dark:text-gray-500">{{ form.color }}</p>
            </div>

            <!-- Ícono -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Ícono *</label>
              <div class="grid grid-cols-6 sm:grid-cols-10 gap-2">
                <button v-for="icon in iconOptions" :key="icon.id" type="button"
                  @click="form.icon_path = icon.d"
                  class="w-10 h-10 rounded-lg border flex items-center justify-center transition-all"
                  :class="form.icon_path === icon.d
                    ? 'bg-indigo-600 border-indigo-600'
                    : 'bg-white dark:bg-[#131314] border-[#E2E8F0] dark:border-[#2A2A2A]'"
                  :title="icon.label">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="1.8"
                    :class="form.icon_path === icon.d ? 'stroke-white' : 'stroke-gray-500 dark:stroke-gray-400'">
                    <path stroke-linecap="round" stroke-linejoin="round" :d="icon.d" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Preview -->
            <div v-if="form.nombre && form.color && form.icon_path" class="flex items-center gap-3 p-4 rounded-xl bg-[#EEF2FA] dark:bg-[#131314] border border-[#E2E8F0] dark:border-[#2A2A2A]">
              <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0" :style="{ background: form.color }">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white" v-html="iconMarkup(form.icon_path)"></svg>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ form.nombre }}</p>
                <p class="text-xs text-gray-400 dark:text-gray-500">Vista previa del tipo</p>
              </div>
            </div>

            <p v-if="formError" class="text-red-600 dark:text-red-400 text-xs">{{ formError }}</p>

            <div class="flex items-center justify-end gap-2 pt-1 border-t border-[#E2E8F0] dark:border-[#2A2A2A] mt-1">
              <button type="button" @click="closeForm"
                class="px-4 py-2 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors focus:outline-none focus-visible:underline">
                Cancelar
              </button>
              <button @click="saveTipo" :disabled="saveLoading || !form.nombre || !form.color || !form.icon_path"
                class="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2">
                <svg v-if="saveLoading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
                {{ saveLoading ? 'Guardando…' : (editingTipo ? 'Guardar cambios' : 'Crear tipo') }}
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- Lista de tipos -->
      <div class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl overflow-hidden">
        <div v-if="tipos.length === 0" class="py-16 text-center">
          <p class="text-sm text-gray-400 dark:text-gray-500">Cargando tipos...</p>
        </div>
        <div v-else class="divide-y divide-[#E2E8F0] dark:divide-[#2A2A2A]">
          <div v-for="t in tipos" :key="t.id"
            class="flex items-center justify-between px-5 py-3.5 hover:bg-[#F5F7FC] dark:hover:bg-[#242424] transition-colors gap-3">
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0" :style="{ background: t.color }">
                <svg class="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white" v-html="iconMarkup(t.icon_path)"></svg>
              </div>
              <div class="min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ t.nombre }}</p>
                  <span v-if="t.builtin" class="px-1.5 py-0.5 rounded-md text-xs font-medium border flex-shrink-0 bg-[#EEF2FA] text-gray-500 border-[#E2E8F0] dark:bg-[#252525] dark:text-gray-400 dark:border-[#2A2A2A]">
                    base
                  </span>
                </div>
                <p class="font-mono text-xs text-gray-400 dark:text-gray-500">{{ t.color }}</p>
              </div>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <button @click="openEdit(t)"
                :aria-label="`Editar ${t.nombre}`" title="Editar"
                class="p-1.5 rounded-lg text-gray-300 dark:text-gray-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 hover:text-indigo-500 dark:hover:text-indigo-400 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487z"/>
                </svg>
              </button>
              <button v-if="!t.builtin" @click="confirmDelete = t"
                :aria-label="`Eliminar ${t.nombre}`" title="Eliminar"
                class="p-1.5 rounded-lg text-gray-300 dark:text-gray-600 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500 dark:hover:text-red-400 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <p class="text-xs text-gray-400 dark:text-gray-600 text-center">
        Los tipos base pueden editarse (nombre, color e ícono) pero no eliminarse.
      </p>

    </div>

    <!-- Delete confirm modal -->
    <div v-if="confirmDelete" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="confirmDelete = null"></div>
      <div class="relative bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-6 max-w-sm w-full shadow-xl">
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">¿Eliminar tipo?</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Se eliminará el tipo:</p>
        <div class="flex items-center gap-3 mb-5 p-3 rounded-xl bg-[#EEF2FA] dark:bg-[#131314]">
          <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0" :style="{ background: confirmDelete.color }">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white" v-html="iconMarkup(confirmDelete.icon_path)"></svg>
          </div>
          <span class="text-sm font-medium text-gray-900 dark:text-white">{{ confirmDelete.nombre }}</span>
        </div>
        <div class="flex gap-3">
          <button @click="confirmDelete = null"
            class="flex-1 py-2 text-sm font-medium rounded-xl border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
            Cancelar
          </button>
          <button @click="doDelete"
            class="flex-1 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-semibold rounded-xl transition-colors">
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
