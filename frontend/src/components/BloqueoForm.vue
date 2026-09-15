<template>
  <form @submit.prevent="submit" class="space-y-4">
    <!-- Tipo de evento -->
    <div>
      <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--form-label,var(--t2))">Tipo de evento *</label>
      <div class="grid grid-cols-2 gap-1.5">
        <button v-for="t in tiposEvento" :key="t.nombre" type="button"
          @click="form.tipo_evento = t.nombre"
          class="flex items-center gap-2 px-3 py-2 rounded-lg border text-xs transition-colors text-left font-medium"
          :style="form.tipo_evento === t.nombre
            ? { background: t.color + '18', borderColor: t.colorBorder, color: t.color }
            : 'background:var(--bg);border-color:var(--border);color:var(--t2)'">
          <div class="w-5 h-5 rounded-full shrink-0 flex items-center justify-center" :style="{ background: t.color }">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
              <path stroke-linecap="round" stroke-linejoin="round" :d="t.iconPath" />
            </svg>
          </div>
          {{ t.nombre }}
        </button>
      </div>
      <p v-if="errors.tipo_evento" class="text-xs mt-1" style="color:#DC2626">{{ errors.tipo_evento }}</p>
    </div>

    <!-- Departamento / Municipio -->
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--form-label,var(--t2))">Departamento *</label>
        <select v-model="form.departamento" @change="onDeptoChange"
          class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
          style="background:var(--bg);border-color:var(--border);color:var(--t1)"
          @focus="$event.target.style.borderColor='var(--accent)'"
          @blur="$event.target.style.borderColor='var(--border)'">
          <option value="">Seleccionar</option>
          <option v-for="d in departamentos" :key="d.nombre" :value="d.nombre">{{ d.nombre }}</option>
        </select>
        <p v-if="errors.departamento" class="text-xs mt-1" style="color:#DC2626">{{ errors.departamento }}</p>
      </div>
      <div>
        <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--form-label,var(--t2))">Municipio *</label>
        <select v-model="form.municipio" @change="onMunicipioChange"
          class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
          style="background:var(--bg);border-color:var(--border);color:var(--t1)"
          @focus="$event.target.style.borderColor='var(--accent)'"
          @blur="$event.target.style.borderColor='var(--border)'">
          <option value="">Seleccionar</option>
          <option v-for="m in municipios" :key="m" :value="m">{{ m }}</option>
        </select>
        <p v-if="errors.municipio" class="text-xs mt-1" style="color:#DC2626">{{ errors.municipio }}</p>
      </div>
    </div>

    <!-- Dirección -->
    <div>
      <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--form-label,var(--t2))">Dirección *</label>
      <div class="flex gap-1 flex-wrap mb-1.5">
        <button v-for="p in prefijos" :key="p" type="button"
          @click="form.direccion = p + ' ' + form.direccion"
          class="px-2 py-0.5 text-xs rounded border transition-colors"
          style="background:var(--bg);border-color:var(--border);color:var(--t2)"
          @mouseover="$event.currentTarget.style.borderColor='var(--accent)'"
          @mouseleave="$event.currentTarget.style.borderColor='var(--border)'">
          {{ p }}
        </button>
      </div>
      <input v-model="form.direccion" type="text" list="dir-history"
        class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
        style="background:var(--bg);border-color:var(--border);color:var(--t1)"
        placeholder="Km. 15 Ruta Nacional 1..."
        @focus="$event.target.style.borderColor='var(--accent)'"
        @blur="$event.target.style.borderColor='var(--border)'" />
      <datalist id="dir-history">
        <option v-for="h in dirHistory" :key="h" :value="h" />
      </datalist>
      <p v-if="errors.direccion" class="text-xs mt-1" style="color:#DC2626">{{ errors.direccion }}</p>
    </div>

    <!-- Coordenadas -->
    <div>
      <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--form-label,var(--t2))">Coordenadas *</label>
      <div class="grid grid-cols-2 gap-2 mb-2">
        <input v-model="form.latitud" type="number" step="any"
          class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border font-mono"
          style="background:var(--bg);border-color:var(--border);color:var(--t1)"
          placeholder="Latitud"
          @focus="$event.target.style.borderColor='var(--accent)'"
          @blur="$event.target.style.borderColor='var(--border)'" />
        <input v-model="form.longitud" type="number" step="any"
          class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border font-mono"
          style="background:var(--bg);border-color:var(--border);color:var(--t1)"
          placeholder="Longitud"
          @focus="$event.target.style.borderColor='var(--accent)'"
          @blur="$event.target.style.borderColor='var(--border)'" />
      </div>
      <button type="button" @click="$emit('toggle-pick-mode')"
        class="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border transition-colors font-medium"
        :style="pickMode
          ? 'background:var(--accent);border-color:var(--accent);color:#fff'
          : 'background:var(--bg);border-color:var(--border);color:var(--t2)'">
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>
        </svg>
        {{ pickMode ? 'Seleccionando en mapa...' : 'Seleccionar en mapa' }}
      </button>
      <p v-if="errors.latitud" class="text-xs mt-1" style="color:#DC2626">{{ errors.latitud }}</p>
    </div>

    <!-- Personas aproximadas -->
    <div>
      <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--form-label,var(--t2))">Personas aproximadas</label>
      <input v-model="form.manifestantes_aproximados" type="number" min="0"
        class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
        style="background:var(--bg);border-color:var(--border);color:var(--t1)"
        placeholder="0"
        @focus="$event.target.style.borderColor='var(--accent)'"
        @blur="$event.target.style.borderColor='var(--border)'" />
    </div>

    <!-- Observaciones -->
    <div>
      <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--form-label,var(--t2))">Observaciones</label>
      <textarea v-model="form.observaciones" rows="3"
        class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border resize-none"
        style="background:var(--bg);border-color:var(--border);color:var(--t1)"
        placeholder="Detalles adicionales..."
        @focus="$event.target.style.borderColor='var(--accent)'"
        @blur="$event.target.style.borderColor='var(--border)'"></textarea>
    </div>

    <!-- Foto -->
    <div>
      <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--form-label,var(--t2))">Foto</label>
      <div v-if="fotoPreview" class="relative mb-2">
        <img :src="fotoPreview" class="w-full h-32 object-cover rounded-lg border" style="border-color:var(--border)" />
        <button type="button" @click="removePhoto"
          class="absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center border"
          style="background:var(--surface);border-color:var(--border);color:var(--t2)">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <label class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors border border-dashed"
        style="background:var(--bg);border-color:var(--border);color:var(--t3)"
        @mouseover="$event.currentTarget.style.borderColor='var(--accent)'"
        @mouseleave="$event.currentTarget.style.borderColor='var(--border)'">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
        </svg>
        <span class="text-xs">{{ fotoFile ? fotoFile.name : 'Subir foto (máx. 5MB)' }}</span>
        <input type="file" accept="image/*" class="hidden" @change="onPhoto" />
      </label>
    </div>

    <div v-if="error" class="text-xs px-3 py-2 rounded-lg" style="background:#FEF2F2;border:1px solid #FECACA;color:#DC2626">{{ error }}</div>

    <button type="submit" :disabled="loading"
      class="w-full py-2.5 text-white font-medium rounded-lg transition-colors text-sm flex items-center justify-center gap-2 disabled:opacity-50"
      style="background:var(--accent)"
      @mouseover="!loading && ($event.currentTarget.style.background='var(--accent-hi)')"
      @mouseleave="$event.currentTarget.style.background='var(--accent)'">
      <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      {{ loading ? 'Registrando...' : 'Registrar evento' }}
    </button>
  </form>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import { departamentos as depList, getMunicipios } from '@/data/guatemala'
import api from '@/api'

const props = defineProps({
  pendingCoords: { type: Object, default: null },
  pickMode: { type: Boolean, default: false },
})
const emit = defineEmits(['created', 'toggle-pick-mode', 'focus-location'])

const { tipos: tiposEvento } = useTiposEvento()
const departamentos = depList

const prefijos = ['Km.', 'Zona', 'Ruta', 'Calle', 'Av.', 'Col.', 'Barrio', 'Aldea', 'Caserío']
const dirHistory = JSON.parse(localStorage.getItem('mv_dir_history') || '[]')

const form = ref({
  tipo_evento: '',
  departamento: '',
  municipio: '',
  direccion: '',
  latitud: '',
  longitud: '',
  manifestantes_aproximados: '',
  observaciones: '',
})
const errors = ref({})
const error = ref('')
const loading = ref(false)
const fotoFile = ref(null)
const fotoPreview = ref(null)

const municipios = computed(() => getMunicipios(form.value.departamento))

function onDeptoChange() {
  form.value.municipio = ''
  const depto = depList.find((d) => d.nombre === form.value.departamento)
  if (depto) emit('focus-location', { ...depto.centro, zoom: 10 })
}

async function onMunicipioChange() {
  const municipio = form.value.municipio
  const departamento = form.value.departamento
  if (!municipio || !departamento) return

  try {
    const q = encodeURIComponent(`${municipio}, ${departamento}, Guatemala`)
    const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${q}&format=json&limit=1&countrycodes=gt`)
    const data = await res.json()
    if (data.length > 0) {
      emit('focus-location', { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon), zoom: 13 })
    }
  } catch {
    const depto = depList.find((d) => d.nombre === departamento)
    if (depto) emit('focus-location', { ...depto.centro, zoom: 12 })
  }
}

function onPhoto(e) {
  const file = e.target.files[0]
  if (!file) return
  fotoFile.value = file
  fotoPreview.value = URL.createObjectURL(file)
}

function removePhoto() {
  fotoFile.value = null
  fotoPreview.value = null
}

watch(() => props.pendingCoords, (coords) => {
  if (coords) {
    form.value.latitud = coords.lat
    form.value.longitud = coords.lng
  }
})

function validate() {
  errors.value = {}
  if (!form.value.tipo_evento) errors.value.tipo_evento = 'Selecciona un tipo'
  if (!form.value.departamento) errors.value.departamento = 'Requerido'
  if (!form.value.municipio) errors.value.municipio = 'Requerido'
  if (!form.value.direccion) errors.value.direccion = 'Requerido'
  if (!form.value.latitud) errors.value.latitud = 'Selecciona ubicación en el mapa'
  return Object.keys(errors.value).length === 0
}

async function submit() {
  if (!validate()) return
  error.value = ''
  loading.value = true
  try {
    const fd = new FormData()
    fd.append('tipo_evento', form.value.tipo_evento)
    fd.append('departamento', form.value.departamento)
    fd.append('municipio', form.value.municipio)
    fd.append('direccion', form.value.direccion)
    fd.append('latitud', form.value.latitud)
    fd.append('longitud', form.value.longitud)
    if (form.value.manifestantes_aproximados) fd.append('manifestantes_aproximados', form.value.manifestantes_aproximados)
    if (form.value.observaciones) fd.append('observaciones', form.value.observaciones)
    if (fotoFile.value) fd.append('foto', fotoFile.value)

    const { data } = await api.post('/api/bloqueos', fd)

    if (form.value.direccion && !dirHistory.includes(form.value.direccion)) {
      dirHistory.unshift(form.value.direccion)
      localStorage.setItem('mv_dir_history', JSON.stringify(dirHistory.slice(0, 20)))
    }

    form.value = { tipo_evento: '', departamento: '', municipio: '', direccion: '', latitud: '', longitud: '', manifestantes_aproximados: '', observaciones: '' }
    fotoFile.value = null
    fotoPreview.value = null
    emit('created', data)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al registrar el evento'
  } finally {
    loading.value = false
  }
}
</script>
