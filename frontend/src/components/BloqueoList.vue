<template>
  <div class="space-y-2">
    <div v-for="b in bloqueos" :key="b.id"
      class="rounded-xl p-4 transition-all border"
      style="background:var(--surface);border-color:var(--border)"
      @mouseover="$event.currentTarget.style.borderColor='var(--accent)'"
      @mouseleave="$event.currentTarget.style.borderColor='var(--border)'">
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
            :style="{ background: getTipoColor(b.tipo_evento) }">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
              <path stroke-linecap="round" stroke-linejoin="round" :d="getTipoIcon(b.tipo_evento)" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm font-medium" style="color:var(--t1)">{{ b.tipo_evento }}</p>
            <p class="text-xs truncate" style="color:var(--t2)">{{ b.municipio }}, {{ b.departamento }}</p>
          </div>
        </div>
        <span class="text-xs px-2 py-0.5 rounded-full font-medium shrink-0 border"
          :style="b.estado === 'Activo'
            ? 'background:#FEF2F2;color:#DC2626;border-color:#FECACA'
            : 'background:#F0FDF4;color:#16A34A;border-color:#BBF7D0'">
          {{ b.estado }}
        </span>
      </div>

      <div class="mt-3 space-y-1 text-xs" style="color:var(--t2)">
        <p class="truncate">📍 {{ b.direccion }}</p>
        <div class="flex items-center gap-2">
          <span class="font-mono" style="color:var(--t3)">{{ Number(b.latitud).toFixed(5) }}, {{ Number(b.longitud).toFixed(5) }}</span>
          <button @click="copyCoords(b)" class="transition-colors" style="color:var(--accent)"
            @mouseover="$event.currentTarget.style.opacity='.7'"
            @mouseleave="$event.currentTarget.style.opacity='1'">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"/>
            </svg>
          </button>
        </div>
        <p v-if="b.manifestantes_aproximados">👥 {{ b.manifestantes_aproximados }} personas aprox.</p>
        <p v-if="b.observaciones" style="color:var(--t3)">{{ b.observaciones }}</p>
        <p class="font-mono" style="color:var(--t3)">{{ timeAgo(b.created_at) }}</p>
      </div>

      <div v-if="canEdit" class="flex items-center gap-2 mt-3 pt-3 border-t" style="border-color:var(--border)">
        <button @click="$emit('focus-event', b)"
          class="flex items-center gap-1 px-2.5 py-1 text-xs rounded-lg transition-colors"
          style="background:var(--bg);color:var(--t2)"
          @mouseover="$event.currentTarget.style.background='var(--border)'"
          @mouseleave="$event.currentTarget.style.background='var(--bg)'">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/></svg>
          Enfocar
        </button>
        <button @click="$emit('edit-event', b)"
          class="flex items-center gap-1 px-2.5 py-1 text-xs rounded-lg transition-colors"
          style="background:var(--bg);color:var(--t2)"
          @mouseover="$event.currentTarget.style.background='var(--border)'"
          @mouseleave="$event.currentTarget.style.background='var(--bg)'">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"/></svg>
          Editar
        </button>
        <button @click="toggleStatus(b)"
          class="flex items-center gap-1 px-2.5 py-1 text-xs rounded-lg transition-colors"
          style="background:var(--bg);color:var(--t2)"
          @mouseover="$event.currentTarget.style.background='var(--border)'"
          @mouseleave="$event.currentTarget.style.background='var(--bg)'">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/></svg>
          {{ b.estado === 'Activo' ? 'Desactivar' : 'Reactivar' }}
        </button>
        <button @click="confirmDelete(b)"
          class="flex items-center gap-1 px-2.5 py-1 text-xs rounded-lg border transition-colors ml-auto"
          style="background:#FEF2F2;color:#DC2626;border-color:#FECACA"
          @mouseover="$event.currentTarget.style.background='#FEE2E2'"
          @mouseleave="$event.currentTarget.style.background='#FEF2F2'">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/></svg>
          Eliminar
        </button>
      </div>
    </div>

    <div v-if="bloqueos.length === 0" class="text-center py-10 text-sm" style="color:var(--t3)">
      No hay eventos
    </div>

    <!-- Delete confirm dialog -->
    <div v-if="toDelete" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="toDelete = null"></div>
      <div class="relative rounded-xl p-6 max-w-sm w-full shadow-xl border" style="background:var(--surface);border-color:var(--border)">
        <h3 class="font-display font-semibold mb-2" style="color:var(--t1)">¿Eliminar evento?</h3>
        <p class="text-sm mb-5" style="color:var(--t2)">Esta acción no se puede deshacer. Se eliminará el evento y su foto.</p>
        <div class="flex gap-3">
          <button @click="toDelete = null"
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
import { ref } from 'vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import api from '@/api'

const props = defineProps({
  bloqueos: { type: Array, default: () => [] },
  canEdit: { type: Boolean, default: false },
})
const emit = defineEmits(['status-changed', 'focus-event', 'edit-event', 'deleted'])

const { getTipo } = useTiposEvento()
const toDelete = ref(null)

function getTipoColor(nombre) {
  return getTipo(nombre)?.color || '#6b7280'
}

function getTipoIcon(nombre) {
  return getTipo(nombre)?.iconPath || ''
}

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'Ahora'
  if (m < 60) return `Hace ${m} min`
  const h = Math.floor(m / 60)
  if (h < 24) return `Hace ${h} h`
  const days = Math.floor(h / 24)
  if (days === 1) return 'Ayer'
  return `Hace ${days} días`
}

async function copyCoords(b) {
  await navigator.clipboard.writeText(`${b.latitud}, ${b.longitud}`)
}

async function toggleStatus(b) {
  const nuevoEstado = b.estado === 'Activo' ? 'Inactivo' : 'Activo'
  const fd = new FormData()
  fd.append('estado', nuevoEstado)
  try {
    const { data } = await api.patch(`/api/bloqueos/${b.id}`, fd)
    emit('status-changed', data)
  } catch {}
}

function confirmDelete(b) {
  toDelete.value = b
}

async function doDelete() {
  if (!toDelete.value) return
  try {
    await api.delete(`/api/bloqueos/${toDelete.value.id}`)
    emit('deleted', toDelete.value.id)
  } catch {}
  toDelete.value = null
}
</script>
