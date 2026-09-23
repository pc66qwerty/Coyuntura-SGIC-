<template>
  <div class="fixed inset-0 z-[3000] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')"></div>

    <div class="relative bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <!-- Franja de color -->
      <div class="h-1.5 w-full sticky top-0 z-10" :style="`background:${tipo.color}`"></div>

      <!-- Header -->
      <div class="sticky top-1.5 z-10 bg-white/95 dark:bg-gray-900/95 backdrop-blur border-b border-gray-200 dark:border-gray-700 px-5 py-4 flex items-start justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0" :style="`background:${tipo.color}22`">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round" :stroke="tipo.color" v-html="tipo.iconPath"></svg>
          </div>
          <div class="min-w-0">
            <h2 class="font-extrabold text-gray-900 dark:text-white uppercase tracking-wide truncate">{{ bloqueo.tipo_evento }}</h2>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-xs font-bold px-2 py-0.5 rounded-full"
                :class="bloqueo.estado === 'Activo' ? 'bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'">
                {{ bloqueo.estado }}
              </span>
              <span class="text-xs text-gray-400 dark:text-gray-500 font-mono">#{{ bloqueo.id }}</span>
            </div>
          </div>
        </div>
        <button @click="$emit('close')" class="p-1.5 rounded-lg text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-300 transition flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="p-5 space-y-6">
        <!-- Fotos -->
        <ImageCarousel v-if="fotos.length" :images="fotos" height="220px" />

        <!-- Ubicación -->
        <div class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-500"></span> Ubicación
          </p>
          <div class="space-y-2 pl-3 text-sm">
            <div>
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Dirección</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.direccion }}</p>
            </div>
            <div>
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Municipio / Departamento</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.municipio }}, {{ bloqueo.departamento }}</p>
            </div>
            <div v-if="conValor(bloqueo.referencia_inicio)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Referencia</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.referencia_inicio }}</p>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div v-if="conValor(bloqueo.zona_inicio)">
                <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Zona</p>
                <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.zona_inicio }}</p>
              </div>
              <div v-if="conValor(bloqueo.comisaria_inicio)">
                <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Comisaría</p>
                <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.comisaria_inicio }}</p>
              </div>
            </div>
            <div>
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Coordenadas</p>
              <p class="text-gray-700 dark:text-gray-300 font-mono">{{ bloqueo.latitud }}, {{ bloqueo.longitud }}</p>
            </div>
          </div>
        </div>

        <!-- Desarrollo del evento -->
        <div class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Desarrollo del evento
          </p>
          <div class="space-y-2 pl-3 text-sm">
            <div class="grid grid-cols-2 gap-3">
              <div v-if="bloqueo.fecha_hora_inicio">
                <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Inicio</p>
                <p class="text-gray-700 dark:text-gray-300">{{ fmtFecha(bloqueo.fecha_hora_inicio) }}</p>
              </div>
              <div v-if="bloqueo.manifestantes_aproximados">
                <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Personas aprox.</p>
                <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.manifestantes_aproximados }}</p>
              </div>
            </div>
            <div v-if="conValor(bloqueo.nivel_conflicto)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1">Nivel de conflicto</p>
              <span class="text-xs font-bold px-2 py-0.5 rounded-full" :class="nivelClase(bloqueo.nivel_conflicto)">{{ bloqueo.nivel_conflicto }}</span>
            </div>
            <div v-if="conValor(bloqueo.demandas)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Demandas / motivo</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.demandas }}</p>
            </div>
            <div v-if="conValor(bloqueo.actores)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Actores</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.actores }}</p>
            </div>
            <div v-if="conValor(bloqueo.instrumentos)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Instrumentos utilizados</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.instrumentos }}</p>
            </div>
            <div v-if="conValor(bloqueo.presencia_policial)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Presencia policial</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.presencia_policial }}</p>
            </div>
            <div v-if="conValor(bloqueo.cantidad_vehiculos)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Cantidad de vehículos</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.cantidad_vehiculos }}</p>
            </div>
            <div v-if="conValor(bloqueo.lideres_vulnerables)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Líderes / menores / tercera edad</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.lideres_vulnerables }}</p>
            </div>
          </div>
        </div>

        <!-- Finalización -->
        <div v-if="tieneFinalizacion" class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Finalización
          </p>
          <div class="space-y-2 pl-3 text-sm">
            <div class="grid grid-cols-2 gap-3">
              <div v-if="bloqueo.fecha_hora_fin">
                <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Finalizó</p>
                <p class="text-gray-700 dark:text-gray-300">{{ fmtFecha(bloqueo.fecha_hora_fin) }}</p>
              </div>
              <div v-if="bloqueo.duracion">
                <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Duración</p>
                <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.duracion }}</p>
              </div>
            </div>
            <div v-if="conValor(bloqueo.direccion_fin)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Dirección de finalización</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.direccion_fin }}</p>
            </div>
            <div v-if="conValor(bloqueo.referencia_fin)">
              <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Referencia de finalización</p>
              <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.referencia_fin }}</p>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div v-if="conValor(bloqueo.departamento_fin) || conValor(bloqueo.municipio_fin)">
                <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Municipio / Depto. fin</p>
                <p class="text-gray-700 dark:text-gray-300">{{ [bloqueo.municipio_fin, bloqueo.departamento_fin].filter(conValor).join(', ') }}</p>
              </div>
              <div v-if="bloqueo.personas_fin">
                <p class="text-[11px] font-mono uppercase tracking-wide text-gray-400 dark:text-gray-500">Personas al finalizar</p>
                <p class="text-gray-700 dark:text-gray-300">{{ bloqueo.personas_fin }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Observaciones -->
        <div v-if="conValor(bloqueo.observaciones)" class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span> Observaciones
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400 italic bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 border-l-2 border-gray-300 dark:border-gray-600 ml-3">
            {{ bloqueo.observaciones }}
          </p>
        </div>

        <!-- Registro -->
        <div class="pt-2 border-t border-gray-100 dark:border-gray-800 text-xs text-gray-400 dark:text-gray-500 font-mono flex flex-wrap gap-x-4 gap-y-1">
          <span>Registrado: {{ fmtFecha(bloqueo.created_at) }}</span>
          <span v-if="bloqueo.updated_at && bloqueo.updated_at !== bloqueo.created_at">Actualizado: {{ fmtFecha(bloqueo.updated_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import ImageCarousel from '@/components/ImageCarousel.vue'

const props = defineProps({
  bloqueo: { type: Object, required: true },
})
defineEmits(['close'])

const { getTipo } = useTiposEvento()
const tipo = computed(() => getTipo(props.bloqueo.tipo_evento) || { color: '#6b7280', iconPath: '' })
const fotos = computed(() => props.bloqueo.fotos || (props.bloqueo.foto_path ? [props.bloqueo.foto_path] : []))

const tieneFinalizacion = computed(() => {
  const b = props.bloqueo
  return !!(b.fecha_hora_fin || conValor(b.direccion_fin) || conValor(b.referencia_fin) || b.personas_fin)
})

function conValor(v) {
  return !!v && v !== 'Por establecer'
}

function fmtFecha(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('es-GT', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function nivelClase(nivel) {
  const n = (nivel || '').toLowerCase()
  if (n === 'alto') return 'bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-400'
  if (n === 'medio') return 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400'
  if (n === 'bajo') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400'
  return 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
}
</script>
