<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/50" @click="$emit('close')"></div>
    <div class="relative rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-xl border" style="background:var(--surface);border-color:var(--border)">
      <!-- Header -->
      <div class="flex items-center justify-between p-5 border-b sticky top-0 z-10" style="background:var(--surface);border-color:var(--border)">
        <h2 class="font-display font-semibold" style="color:var(--t1)">Editar evento</h2>
        <button @click="$emit('close')" class="transition-colors" style="color:var(--t3)"
          @mouseover="$event.currentTarget.style.color='var(--t1)'"
          @mouseleave="$event.currentTarget.style.color='var(--t3)'">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <form @submit.prevent="submit" class="p-5 space-y-4">
        <!-- Estado toggle -->
        <div class="flex items-center justify-between rounded-lg px-4 py-3 border" style="background:var(--bg);border-color:var(--border)">
          <span class="text-sm font-medium" style="color:var(--t1)">Estado del evento</span>
          <button type="button" @click="form.estado = form.estado === 'Activo' ? 'Finalizado' : 'Activo'"
            class="px-3 py-1 rounded-full text-xs font-medium transition-colors border"
            :style="form.estado === 'Activo'
              ? 'background:#FEF2F2;color:#DC2626;border-color:#FECACA'
              : 'background:#F0FDF4;color:#16A34A;border-color:#BBF7D0'">
            {{ form.estado }}
          </button>
        </div>

        <!-- Tipo -->
        <div>
          <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Tipo de evento</label>
          <div class="grid grid-cols-2 gap-1.5">
            <button v-for="t in tiposEvento" :key="t.nombre" type="button"
              @click="form.tipo_evento = t.nombre"
              class="flex items-center gap-2 px-3 py-2 rounded-lg border text-xs transition-colors text-left font-medium"
              :style="form.tipo_evento === t.nombre
                ? { background: t.color + '18', borderColor: t.colorBorder, color: t.color }
                : 'background:var(--bg);border-color:var(--border);color:var(--t2)'">
              <div class="w-4 h-4 rounded-full shrink-0" :style="{ background: t.color }"></div>
              {{ t.nombre }}
            </button>
          </div>
        </div>

        <!-- Depto / Municipio -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Departamento</label>
            <select v-model="form.departamento" @change="form.municipio = ''"
              class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'">
              <option v-for="d in departamentos" :key="d.nombre" :value="d.nombre">{{ d.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Municipio</label>
            <select v-model="form.municipio"
              class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'">
              <option v-for="m in municipios" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>
        </div>

        <!-- Dirección -->
        <div>
          <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Dirección</label>
          <input v-model="form.direccion" type="text"
            class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
            style="background:var(--bg);border-color:var(--border);color:var(--t1)"
            @focus="$event.target.style.borderColor='var(--accent)'"
            @blur="$event.target.style.borderColor='var(--border)'" />
        </div>

        <!-- Coordenadas -->
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Latitud</label>
            <input v-model="form.latitud" type="number" step="any"
              class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border font-mono"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'" />
          </div>
          <div>
            <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Longitud</label>
            <input v-model="form.longitud" type="number" step="any"
              class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border font-mono"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'" />
          </div>
        </div>

        <!-- Personas -->
        <div>
          <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Personas aproximadas</label>
          <input v-model="form.manifestantes_aproximados" type="number" min="0"
            class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
            style="background:var(--bg);border-color:var(--border);color:var(--t1)"
            @focus="$event.target.style.borderColor='var(--accent)'"
            @blur="$event.target.style.borderColor='var(--border)'" />
        </div>

        <!-- Observaciones -->
        <div>
          <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Observaciones</label>
          <textarea v-model="form.observaciones" rows="3"
            class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border resize-none"
            style="background:var(--bg);border-color:var(--border);color:var(--t1)"
            @focus="$event.target.style.borderColor='var(--accent)'"
            @blur="$event.target.style.borderColor='var(--border)'"></textarea>
        </div>

        <!-- Foto -->
        <div>
          <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Foto</label>
          <div v-if="fotoPreview" class="relative mb-2">
            <img :src="fotoPreview" class="w-full h-32 object-cover rounded-lg border" style="border-color:var(--border)" />
            <button type="button" @click="removePhoto"
              class="absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center border"
              style="background:var(--surface);border-color:var(--border);color:var(--t2)">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div v-else-if="bloqueo.foto_path && !removeOldPhoto" class="relative mb-2">
            <img :src="apiBase + bloqueo.foto_path" class="w-full h-32 object-cover rounded-lg border" style="border-color:var(--border)" />
            <button type="button" @click="removeOldPhoto = true"
              class="absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center border"
              style="background:var(--surface);border-color:#FECACA;color:#DC2626">
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
            <span class="text-xs">{{ fotoFile ? fotoFile.name : 'Subir nueva foto' }}</span>
            <input type="file" accept="image/*" class="hidden" @change="onPhoto" />
          </label>
        </div>

        <div v-if="error" class="text-xs px-3 py-2 rounded-lg" style="background:#FEF2F2;border:1px solid #FECACA;color:#DC2626">{{ error }}</div>

        <div class="flex gap-3 pt-2">
          <button type="button" @click="$emit('close')"
            class="flex-1 py-2.5 text-sm font-medium rounded-lg border transition-colors"
            style="background:var(--bg);border-color:var(--border);color:var(--t2)">
            Cancelar
          </button>
          <button type="submit" :disabled="loading"
            class="flex-1 py-2.5 text-white font-medium rounded-lg transition-colors text-sm flex items-center justify-center gap-2 disabled:opacity-50"
            style="background:var(--accent)"
            @mouseover="!loading && ($event.currentTarget.style.background='var(--accent-hi)')"
            @mouseleave="$event.currentTarget.style.background='var(--accent)'">
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ loading ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import { departamentos as depList, getMunicipios } from '@/data/guatemala'
import api from '@/api'

const props = defineProps({ bloqueo: { type: Object, required: true } })
const emit = defineEmits(['updated', 'close'])

const { tipos: tiposEvento } = useTiposEvento()
const departamentos = depList
const apiBase = import.meta.env.VITE_API_URL || ''

const form = ref({ ...props.bloqueo })
const fotoFile = ref(null)
const fotoPreview = ref(null)
const removeOldPhoto = ref(false)
const loading = ref(false)
const error = ref('')

const municipios = computed(() => getMunicipios(form.value.departamento))

function onPhoto(e) {
  const file = e.target.files[0]
  if (!file) return
  fotoFile.value = file
  fotoPreview.value = URL.createObjectURL(file)
  removeOldPhoto.value = false
}

function removePhoto() {
  fotoFile.value = null
  fotoPreview.value = null
}

async function submit() {
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
    fd.append('estado', form.value.estado)
    if (form.value.manifestantes_aproximados != null) fd.append('manifestantes_aproximados', form.value.manifestantes_aproximados)
    if (form.value.observaciones != null) fd.append('observaciones', form.value.observaciones)
    if (removeOldPhoto.value) fd.append('remove_foto', 'true')
    if (fotoFile.value) fd.append('foto', fotoFile.value)

    const { data } = await api.patch(`/api/bloqueos/${props.bloqueo.id}`, fd)
    emit('updated', data)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al guardar'
  } finally {
    loading.value = false
  }
}
</script>
