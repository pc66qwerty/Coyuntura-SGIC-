<template>
  <div class="relative w-full h-full">
    <div ref="mapEl" class="w-full h-full"></div>
    <!-- Map theme toggle -->
    <button @click="toggleTileTheme"
      class="absolute top-3 right-3 z-[1000] px-2.5 py-1 rounded-lg text-xs transition-colors font-mono border"
      style="background:var(--surface);border-color:var(--border);color:var(--t2)">
      {{ darkTile ? '🌙 Oscuro' : '☀️ Claro' }}
    </button>
    <div v-if="pickMode" class="absolute inset-0 z-[900] pointer-events-none">
      <div class="absolute top-3 left-1/2 -translate-x-1/2 px-4 py-1.5 rounded-full text-xs font-medium shadow-lg text-white"
        style="background:var(--accent)">
        Haz clic en el mapa para seleccionar la ubicación
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  bloqueos: { type: Array, default: () => [] },
  pickMode: { type: Boolean, default: false },
})
const emit = defineEmits(['coords-selected'])

const { buildMarkerHtml, load } = useTiposEvento()

const mapEl = ref(null)
const darkTile = ref(localStorage.getItem('mapTheme') === 'dark')

let map = null
let markers = {}
let tempMarker = null
let tileLayer = null

const DARK_TILE = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
const LIGHT_TILE = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

function toggleTileTheme() {
  darkTile.value = !darkTile.value
  localStorage.setItem('mapTheme', darkTile.value ? 'dark' : 'light')
  if (map && tileLayer) {
    map.removeLayer(tileLayer)
    tileLayer = L.tileLayer(darkTile.value ? DARK_TILE : LIGHT_TILE, { maxZoom: 19, attribution: '' })
    tileLayer.addTo(map)
  }
}

function renderMarkers(list) {
  if (!map) return
  const ids = new Set(list.map((b) => b.id))

  Object.keys(markers).forEach((id) => {
    if (!ids.has(Number(id))) {
      map.removeLayer(markers[id])
      delete markers[id]
    }
  })

  list.forEach((b) => {
    const icon = L.divIcon({
      html: buildMarkerHtml(b.tipo_evento, b.estado === 'Activo'),
      className: '',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    })
    const popup = `
      <div style="font-size:12px;color:#e5e7eb;min-width:180px;">
        <strong style="color:#fff">${b.tipo_evento}</strong>
        <span style="margin-left:6px;padding:1px 6px;border-radius:9999px;font-size:10px;background:${b.estado === 'Activo' ? '#7f1d1d' : '#14532d'};color:${b.estado === 'Activo' ? '#fca5a5' : '#86efac'}">${b.estado}</span>
        <br/><span style="color:#9ca3af">${b.municipio}, ${b.departamento}</span>
        <br/><span style="color:#9ca3af">${b.direccion}</span>
        ${b.foto_path ? `<br/><img src="${b.foto_path}" style="width:100%;margin-top:6px;border-radius:4px;max-height:100px;object-fit:cover" />` : ''}
      </div>
    `
    if (markers[b.id]) {
      markers[b.id].setIcon(icon)
    } else {
      const m = L.marker([b.latitud, b.longitud], { icon })
      m.bindPopup(popup, { className: 'dark-popup' })
      m.addTo(map)
      markers[b.id] = m
    }
  })
}

function focusOn(lat, lng, zoom = 14) {
  if (map) map.setView([lat, lng], zoom)
}

function clearTempMarker() {
  if (tempMarker && map) {
    map.removeLayer(tempMarker)
    tempMarker = null
  }
}

defineExpose({ focusOn, clearTempMarker, mapEl })

onMounted(async () => {
  await load()
  map = L.map(mapEl.value, {
    center: [14.6349, -90.5069],
    zoom: 7,
    zoomControl: false,
  })
  L.control.zoom({ position: 'bottomleft' }).addTo(map)
  tileLayer = L.tileLayer(darkTile.value ? DARK_TILE : LIGHT_TILE, { maxZoom: 19, attribution: '' })
  tileLayer.addTo(map)

  map.on('click', (e) => {
    if (!props.pickMode) return
    clearTempMarker()
    const { lat, lng } = e.latlng
    const tempIcon = L.divIcon({
      html: `<div style="width:28px;height:28px;border-radius:50%;background:var(--accent,#1E3A5F);border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="white" style="width:14px;height:14px;">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>
        </svg>
      </div>`,
      className: '',
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    })
    tempMarker = L.marker([lat, lng], { icon: tempIcon }).addTo(map)
    emit('coords-selected', { lat: lat.toFixed(6), lng: lng.toFixed(6) })
  })

  renderMarkers(props.bloqueos)
})

onUnmounted(() => {
  if (map) map.remove()
})

watch(() => props.bloqueos, (list) => renderMarkers(list), { deep: true })
</script>

<style>
.dark-popup .leaflet-popup-content-wrapper {
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}
.dark-popup .leaflet-popup-tip {
  background: #1f2937;
}
</style>
