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
          <button type="button" @click="form.estado = form.estado === 'Activo' ? 'Inactivo' : 'Activo'"
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
        <button type="button" @click="$emit('toggle-pick-mode')"
          class="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border transition-colors font-medium -mt-1"
          :style="pickMode
            ? 'background:var(--accent);border-color:var(--accent);color:#fff'
            : 'background:var(--bg);border-color:var(--border);color:var(--t2)'">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>
          </svg>
          {{ pickMode ? 'Cierra este panel y haz clic en el mapa...' : 'Seleccionar en mapa' }}
        </button>

        <!-- Personas -->
        <div>
          <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Personas aproximadas</label>
          <input v-model="form.manifestantes_aproximados" type="number" min="0"
            class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
            style="background:var(--bg);border-color:var(--border);color:var(--t1)"
            @focus="$event.target.style.borderColor='var(--accent)'"
            @blur="$event.target.style.borderColor='var(--border)'" />
        </div>

        <!-- Datos del evento (matriz institucional) -->
        <div class="rounded-lg border" style="border-color:var(--border)">
          <button type="button" @click="showDatosEvento = !showDatosEvento"
            class="w-full flex items-center justify-between px-3 py-2.5 text-left" style="color:var(--t2)">
            <span class="font-mono text-xs uppercase tracking-wide">Datos del evento <span style="color:var(--t3)">(opcional)</span></span>
            <svg class="w-4 h-4 transition-transform" :class="showDatosEvento ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          <div v-if="showDatosEvento" class="p-3 pt-0 space-y-3 border-t" style="border-color:var(--border)">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Fecha y hora de inicio</label>
                <input v-model="form.fecha_hora_inicio" type="datetime-local"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Nivel de conflicto</label>
                <select v-model="form.nivel_conflicto"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)">
                  <option value="">Por establecer</option>
                  <option value="Bajo">Bajo</option>
                  <option value="Medio">Medio</option>
                  <option value="Alto">Alto</option>
                </select>
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Zona</label>
                <input v-model="form.zona_inicio" type="text" placeholder="Ej. 7"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Comisaría</label>
                <input v-model="form.comisaria_inicio" type="text" placeholder="Ej. 14"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
            </div>
            <div>
              <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Referencia del punto</label>
              <input v-model="form.referencia_inicio" type="text" placeholder="Punto de referencia del lugar"
                class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Instrumentos utilizados</label>
                <input v-model="form.instrumentos" type="text" placeholder="Pancartas, llantas, palos..."
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Presencia policial</label>
                <input v-model="form.presencia_policial" type="text" placeholder="Efectivos y unidades"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Cantidad de vehículos</label>
                <input v-model="form.cantidad_vehiculos" type="text" placeholder="Ej. 6 vehículos"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Actores</label>
                <input v-model="form.actores" type="text" placeholder="Ej. Civiles"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
            </div>
            <div>
              <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Demandas / motivo</label>
              <input v-model="form.demandas" type="text" placeholder="Ej. Por alza en precios del combustible"
                class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
            </div>
            <div>
              <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Líderes identificados / menores / tercera edad</label>
              <input v-model="form.lideres_vulnerables" type="text" placeholder="Detalle si aplica"
                class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
            </div>
          </div>
        </div>

        <!-- Finalización -->
        <div class="rounded-lg border" style="border-color:var(--border)">
          <button type="button" @click="showFinalizacion = !showFinalizacion"
            class="w-full flex items-center justify-between px-3 py-2.5 text-left" style="color:var(--t2)">
            <span class="font-mono text-xs uppercase tracking-wide">Finalización <span style="color:var(--t3)">(opcional)</span></span>
            <svg class="w-4 h-4 transition-transform" :class="showFinalizacion ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          <div v-if="showFinalizacion" class="p-3 pt-0 space-y-3 border-t" style="border-color:var(--border)">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Fecha y hora de finalización</label>
                <input v-model="form.fecha_hora_fin" type="datetime-local"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Personas al finalizar</label>
                <input v-model="form.personas_fin" type="number" min="0"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
            </div>
            <div>
              <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Dirección de finalización</label>
              <input v-model="form.direccion_fin" type="text" placeholder="Si es distinta al punto de inicio"
                class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
            </div>
            <div>
              <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Referencia de finalización</label>
              <input v-model="form.referencia_fin" type="text"
                class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Latitud fin</label>
                <input v-model="form.latitud_fin" type="number" step="any"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border font-mono"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Longitud fin</label>
                <input v-model="form.longitud_fin" type="number" step="any"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border font-mono"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Departamento fin</label>
                <select v-model="form.departamento_fin"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)">
                  <option value="">—</option>
                  <option v-for="d in departamentos" :key="d.nombre" :value="d.nombre">{{ d.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Municipio fin</label>
                <select v-model="form.municipio_fin"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)">
                  <option value="">—</option>
                  <option v-for="m in municipiosFin" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Zona fin</label>
                <input v-model="form.zona_fin" type="text"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
              <div>
                <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">Comisaría fin</label>
                <input v-model="form.comisaria_fin" type="text"
                  class="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors border"
                  style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
              </div>
            </div>
            <p v-if="duracionCalculada" class="text-xs font-mono" style="color:var(--t3)">Duración: {{ duracionCalculada }}</p>
          </div>
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

        <!-- Fotos -->
        <div>
          <label class="block font-mono text-xs uppercase tracking-wide mb-1.5" style="color:var(--t3)">
            Fotos <span style="color:var(--t3)">({{ existingFotos.length + newPreviews.length }}/{{ MAX_FOTOS }})</span>
          </label>

          <div v-if="existingFotos.length || newPreviews.length" class="grid grid-cols-4 gap-2 mb-2">
            <div v-for="src in existingFotos" :key="src" class="relative">
              <img :src="src" class="w-full h-16 object-cover rounded-lg border" style="border-color:var(--border)" />
              <button type="button" @click="markRemoveExisting(src)"
                class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full flex items-center justify-center border"
                style="background:var(--surface);border-color:#FECACA;color:#DC2626">
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
            <div v-for="(src, i) in newPreviews" :key="src" class="relative">
              <img :src="src" class="w-full h-16 object-cover rounded-lg border" style="border-color:var(--border)" />
              <button type="button" @click="removeNewPhoto(i)"
                class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full flex items-center justify-center border"
                style="background:var(--surface);border-color:var(--border);color:var(--t2)">
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>

          <label v-if="existingFotos.length + newPreviews.length < MAX_FOTOS"
            class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors border border-dashed"
            style="background:var(--bg);border-color:var(--border);color:var(--t3)"
            @mouseover="$event.currentTarget.style.borderColor='var(--accent)'"
            @mouseleave="$event.currentTarget.style.borderColor='var(--border)'">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
            </svg>
            <span class="text-xs">Agregar fotos (máx. {{ MAX_FOTOS }})</span>
            <input type="file" accept="image/*" multiple class="hidden" @change="onPhoto" />
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
import { ref, computed, watch } from 'vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import { departamentos as depList, getMunicipios } from '@/data/guatemala'
import api from '@/api'

const props = defineProps({
  bloqueo: { type: Object, required: true },
  pendingCoords: { type: Object, default: null },
  pickMode: { type: Boolean, default: false },
})
const emit = defineEmits(['updated', 'close', 'toggle-pick-mode'])

const { tipos: tiposEvento } = useTiposEvento()
const departamentos = depList
const apiBase = import.meta.env.VITE_API_URL || ''

function toDatetimeLocal(iso) {
  if (!iso) return ''
  return iso.slice(0, 16)
}

const form = ref({
  ...props.bloqueo,
  fecha_hora_inicio: toDatetimeLocal(props.bloqueo.fecha_hora_inicio),
  fecha_hora_fin: toDatetimeLocal(props.bloqueo.fecha_hora_fin),
})
const showDatosEvento = ref(false)
const showFinalizacion = ref(false)
const MAX_FOTOS = 8
const existingFotos = ref((props.bloqueo.fotos && props.bloqueo.fotos.length ? props.bloqueo.fotos : (props.bloqueo.foto_path ? [props.bloqueo.foto_path] : [])).map((p) => apiBase + p))
const fotosARemover = ref([])
const newFiles = ref([])
const newPreviews = ref([])
const loading = ref(false)
const error = ref('')

const municipios = computed(() => getMunicipios(form.value.departamento))
const municipiosFin = computed(() => getMunicipios(form.value.departamento_fin))

watch(() => props.pendingCoords, (coords) => {
  if (coords) {
    form.value.latitud = coords.lat
    form.value.longitud = coords.lng
  }
})

const duracionCalculada = computed(() => {
  if (!form.value.fecha_hora_inicio || !form.value.fecha_hora_fin) return null
  const inicio = new Date(form.value.fecha_hora_inicio)
  const fin = new Date(form.value.fecha_hora_fin)
  const diffMin = Math.round((fin - inicio) / 60000)
  if (isNaN(diffMin) || diffMin < 0) return null
  const horas = Math.floor(diffMin / 60)
  const minutos = diffMin % 60
  if (horas && minutos) return `${horas}h ${minutos}min`
  if (horas) return `${horas}h`
  return `${minutos}min`
})

function onPhoto(e) {
  const files = Array.from(e.target.files || [])
  const espacio = MAX_FOTOS - existingFotos.value.length - newFiles.value.length
  files.slice(0, espacio).forEach((file) => {
    newFiles.value.push(file)
    newPreviews.value.push(URL.createObjectURL(file))
  })
  e.target.value = ''
}

function removeNewPhoto(i) {
  URL.revokeObjectURL(newPreviews.value[i])
  newFiles.value.splice(i, 1)
  newPreviews.value.splice(i, 1)
}

function markRemoveExisting(displaySrc) {
  const idx = existingFotos.value.indexOf(displaySrc)
  if (idx === -1) return
  const originalPath = displaySrc.slice(apiBase.length)
  fotosARemover.value.push(originalPath)
  existingFotos.value.splice(idx, 1)
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

    const CAMPOS_MATRIZ = [
      'fecha_hora_inicio', 'referencia_inicio', 'zona_inicio', 'comisaria_inicio',
      'instrumentos', 'nivel_conflicto', 'presencia_policial', 'cantidad_vehiculos',
      'demandas', 'actores', 'lideres_vulnerables',
      'fecha_hora_fin', 'direccion_fin', 'latitud_fin', 'longitud_fin', 'referencia_fin',
      'departamento_fin', 'municipio_fin', 'zona_fin', 'comisaria_fin', 'personas_fin',
    ]
    CAMPOS_MATRIZ.forEach((key) => {
      const val = form.value[key]
      if (val !== null && val !== undefined && val !== '') fd.append(key, val)
    })

    fotosARemover.value.forEach((path) => fd.append('remove_fotos', path))
    newFiles.value.forEach((file) => fd.append('fotos', file))

    const { data } = await api.patch(`/api/bloqueos/${props.bloqueo.id}`, fd)
    emit('updated', data)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al guardar'
  } finally {
    loading.value = false
  }
}
</script>
