<template>
  <div class="min-h-screen" style="background:var(--bg)">
    <header class="border-b sticky top-0 z-20" style="background:var(--surface);border-color:var(--border)">
      <div class="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <router-link to="/dashboard" class="transition-colors" style="color:var(--t2)">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
            </svg>
          </router-link>
          <span class="font-display font-semibold" style="color:var(--t1)">Tipos de evento</span>
          <span class="font-mono text-xs px-2 py-0.5 rounded-full border" style="color:var(--t2);background:var(--bg);border-color:var(--border)">
            {{ tipos.length }} tipos
          </span>
        </div>
        <button @click="showForm = !showForm"
          class="flex items-center gap-2 px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors"
          style="background:var(--accent)"
          @mouseover="$event.currentTarget.style.background='var(--accent-hi)'"
          @mouseleave="$event.currentTarget.style.background='var(--accent)'">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Nuevo tipo
        </button>
      </div>
    </header>

    <div class="max-w-3xl mx-auto px-6 py-8 space-y-6">

      <!-- Create form -->
      <div v-if="showForm" class="rounded-xl p-6 border" style="background:var(--surface);border-color:var(--border)">
        <h2 class="font-display font-semibold mb-5" style="color:var(--t1)">Crear tipo de evento</h2>
        <div class="space-y-5">
          <!-- Nombre -->
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t2)">Nombre *</label>
            <input v-model="form.nombre" type="text" placeholder="Ej: Caminata, Maratón..."
              class="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'" />
          </div>

          <!-- Color -->
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-2" style="color:var(--t2)">Color *</label>
            <div class="flex flex-wrap gap-2">
              <button v-for="c in colorPalette" :key="c" type="button"
                @click="form.color = c"
                class="w-8 h-8 rounded-full border-2 transition-all"
                :style="{ background: c, borderColor: form.color === c ? 'var(--t1)' : 'transparent' }">
              </button>
              <label class="w-8 h-8 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all overflow-hidden"
                :style="{ background: form.color, borderColor: 'var(--border)' }" title="Color personalizado">
                <input type="color" v-model="form.color" class="opacity-0 absolute w-0 h-0" />
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487z"/>
                </svg>
              </label>
            </div>
            <p class="font-mono text-xs mt-1.5" style="color:var(--t3)">{{ form.color }}</p>
          </div>

          <!-- Ícono -->
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-2" style="color:var(--t2)">Ícono *</label>
            <div class="grid grid-cols-6 sm:grid-cols-10 gap-2">
              <button v-for="icon in iconOptions" :key="icon.id" type="button"
                @click="form.icon_path = icon.d"
                class="w-10 h-10 rounded-lg border flex items-center justify-center transition-all"
                :style="form.icon_path === icon.d
                  ? 'background:var(--accent);border-color:var(--accent)'
                  : 'background:var(--bg);border-color:var(--border)'"
                :title="icon.label">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="1.8"
                  :stroke="form.icon_path === icon.d ? 'white' : 'var(--t2)'">
                  <path stroke-linecap="round" stroke-linejoin="round" :d="icon.d" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Preview -->
          <div v-if="form.nombre && form.color && form.icon_path" class="flex items-center gap-3 p-4 rounded-lg border" style="background:var(--bg);border-color:var(--border)">
            <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0" :style="{ background: form.color }">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
                <path stroke-linecap="round" stroke-linejoin="round" :d="form.icon_path" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-sm" style="color:var(--t1)">{{ form.nombre }}</p>
              <p class="text-xs" style="color:var(--t3)">Vista previa del tipo</p>
            </div>
          </div>

          <div v-if="formError" class="text-xs px-3 py-2 rounded-lg" style="background:#FEF2F2;border:1px solid #FECACA;color:#DC2626">{{ formError }}</div>

          <div class="flex gap-3">
            <button type="button" @click="showForm = false"
              class="px-5 py-2 text-sm rounded-lg border transition-colors"
              style="background:var(--bg);border-color:var(--border);color:var(--t2)">
              Cancelar
            </button>
            <button @click="createTipo" :disabled="createLoading || !form.nombre || !form.color || !form.icon_path"
              class="px-5 py-2 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
              style="background:var(--accent)">
              <svg v-if="createLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ createLoading ? 'Creando...' : 'Crear tipo' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Types grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div v-for="t in tipos" :key="t.id"
          class="flex items-center gap-3 rounded-xl p-4 border"
          style="background:var(--surface);border-color:var(--border)">
          <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0" :style="{ background: t.color }">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
              <path stroke-linecap="round" stroke-linejoin="round" :d="t.icon_path" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-sm" style="color:var(--t1)">{{ t.nombre }}</p>
            <p class="font-mono text-xs" style="color:var(--t3)">{{ t.color }}</p>
          </div>
          <button v-if="!t.builtin" @click="confirmDelete = t"
            class="p-1.5 rounded-lg transition-colors shrink-0"
            style="color:#DC2626"
            @mouseover="$event.currentTarget.style.background='#FEF2F2'"
            @mouseleave="$event.currentTarget.style.background='transparent'">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
            </svg>
          </button>
          <span v-else class="font-mono text-xs px-2 py-0.5 rounded border" style="color:var(--t3);border-color:var(--border)">base</span>
        </div>

        <div v-if="tipos.length === 0" class="col-span-2 text-center py-10 text-sm" style="color:var(--t3)">
          Cargando tipos...
        </div>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <div v-if="confirmDelete" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="confirmDelete = null"></div>
      <div class="relative rounded-xl p-6 max-w-sm w-full border shadow-xl" style="background:var(--surface);border-color:var(--border)">
        <h3 class="font-display font-semibold mb-2" style="color:var(--t1)">¿Eliminar tipo?</h3>
        <p class="text-sm mb-1" style="color:var(--t2)">Se eliminará el tipo:</p>
        <div class="flex items-center gap-3 mb-5 p-3 rounded-lg" style="background:var(--bg)">
          <div class="w-8 h-8 rounded-full flex items-center justify-center" :style="{ background: confirmDelete.color }">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
              <path stroke-linecap="round" stroke-linejoin="round" :d="confirmDelete.icon_path" />
            </svg>
          </div>
          <span class="font-medium text-sm" style="color:var(--t1)">{{ confirmDelete.nombre }}</span>
        </div>
        <div class="flex gap-3">
          <button @click="confirmDelete = null"
            class="flex-1 py-2 text-sm rounded-lg border transition-colors"
            style="background:var(--bg);border-color:var(--border);color:var(--t2)">Cancelar</button>
          <button @click="doDelete"
            class="flex-1 py-2 text-white text-sm rounded-lg transition-colors"
            style="background:#DC2626">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const tipos = ref([])
const showForm = ref(false)
const confirmDelete = ref(null)
const createLoading = ref(false)
const formError = ref('')

const form = ref({ nombre: '', color: '#2563EB', icon_path: '' })

const colorPalette = [
  '#DC2626', '#EA580C', '#D97706', '#CA8A04',
  '#16A34A', '#0D9488', '#2563EB', '#7C3AED',
  '#DB2777', '#475569',
]

const iconOptions = [
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

async function fetchTipos() {
  try {
    const { data } = await api.get('/api/tipos-evento')
    tipos.value = data.map((t) => ({ ...t, builtin: BUILTIN.includes(t.nombre) }))
  } catch {}
}

async function createTipo() {
  formError.value = ''
  if (!form.value.nombre.trim()) { formError.value = 'El nombre es requerido'; return }
  createLoading.value = true
  try {
    const fd = new FormData()
    fd.append('nombre', form.value.nombre.trim())
    fd.append('color', form.value.color)
    fd.append('color_light', makeLight(form.value.color))
    fd.append('color_border', makeBorder(form.value.color))
    fd.append('icon_path', form.value.icon_path)
    const { data } = await api.post('/api/tipos-evento', fd)
    tipos.value.push({ ...data, builtin: false })
    tipos.value.sort((a, b) => a.nombre.localeCompare(b.nombre))
    form.value = { nombre: '', color: '#2563EB', icon_path: '' }
    showForm.value = false
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Error al crear el tipo'
  } finally {
    createLoading.value = false
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
