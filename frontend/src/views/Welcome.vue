<script setup>
import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import { useTiposEvento } from '@/composables/useTiposEvento'
import ImageCarousel from '@/components/ImageCarousel.vue'
import EventDetailModal from '@/components/EventDetailModal.vue'
import AppFooter from '@/components/AppFooter.vue'
import api from '@/api'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

const GT_BOUNDS = L.latLngBounds([13.74, -92.30], [17.82, -88.15])
const GT_CENTER = [15.30, -90.25]

const router = useRouter()
const auth = useAuthStore()

// ─── UI Theme ──────────────────────────────────────────────────────────
const { theme, apply: applyTheme } = useTheme()
const { tipos, getTipo, buildMarkerHtml, load: loadTipos } = useTiposEvento()

function toggleUITheme() {
  applyTheme(theme.value === 'dark' ? 'light' : 'dark')
}

function logout() {
  auth.logout()
  router.push('/login')
}

// ─── Estado ────────────────────────────────────────────────────────────
const mapContainer = ref(null)
const bloqueos = ref([])
const selectedBloqueo = ref(null)
const detailBloqueo = ref(null)
const searchQuery = ref('')
const filterEstado = ref('Todos')
const filterTipo = ref('Todos')
const filterDepto = ref('Todos')
const filterPeriodo = ref('todo')   // 'hoy' | 'ayer' | 'semana' | 'mes' | 'todo' | 'custom'
const filterDesde = ref('')
const filterHasta = ref('')
const sortBy = ref('reciente') // 'reciente' | 'antiguo' | 'activos'
const lastUpdated = ref(null)
const ticking = ref(false)
const newEventAlert = ref(null) // { tipo_evento, municipio, departamento }
let alertTimeout = null
let selectedTimeout = null
const SELECTED_CARD_TIMEOUT = 15000

function selectBloqueo(b) {
  selectedBloqueo.value = b
  clearTimeout(selectedTimeout)
  if (b) selectedTimeout = setTimeout(() => { selectedBloqueo.value = null }, SELECTED_CARD_TIMEOUT)
}

function deselectBloqueo() {
  selectedBloqueo.value = null
  clearTimeout(selectedTimeout)
}

// Contadores animados
const displayCount = ref({ total: 0, activos: 0, finalizados: 0, tipos: 0 })

const mapDark = ref(localStorage.getItem('mapTheme') === 'dark')
const TILES = {
  dark: { url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', attribution: '&copy; Esri &copy; OpenStreetMap contributors' },
  light: { url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' },
}

let map, tileLayer, markerLayer, pollInterval, tickInterval

const toggleTheme = () => {
  mapDark.value = !mapDark.value
  localStorage.setItem('mapTheme', mapDark.value ? 'dark' : 'light')
  if (map && tileLayer) {
    map.removeLayer(tileLayer)
    const t = TILES[mapDark.value ? 'dark' : 'light']
    tileLayer = L.tileLayer(t.url, { attribution: t.attribution, maxZoom: 19 }).addTo(map)
  }
}

// ─── Helpers de fecha ─────────────────────────────────────────────────
const startOfDay = (d) => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x }

const formatFechaRelativa = (iso) => {
  if (!iso) return null
  const diff = Math.floor((Date.now() - new Date(iso)) / 1000)
  if (diff < 60) return 'hace un momento'
  if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)} h`
  const dias = Math.floor(diff / 86400)
  if (dias === 1) return 'ayer'
  if (dias < 7) return `hace ${dias} días`
  if (dias < 30) return `hace ${Math.floor(dias / 7)} sem.`
  return new Date(iso).toLocaleDateString('es-GT', { day: '2-digit', month: 'short' })
}

const formatFechaCorta = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('es-GT', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// ─── Computed ──────────────────────────────────────────────────────────
const activos = computed(() => bloqueos.value.filter(b => b.estado === 'Activo').length)
const finalizados = computed(() => bloqueos.value.filter(b => b.estado === 'Inactivo').length)

const tiposConteo = computed(() => {
  const m = {}
  bloqueos.value.forEach(b => { m[b.tipo_evento] = (m[b.tipo_evento] || 0) + 1 })
  return m
})

// Departamentos únicos en los eventos cargados
const deptosDisponibles = computed(() => {
  const set = new Set(bloqueos.value.map(b => b.departamento).filter(Boolean))
  return ['Todos', ...Array.from(set).sort()]
})

const hayFiltrosActivos = computed(() =>
  searchQuery.value || filterEstado.value !== 'Todos' || filterTipo.value !== 'Todos' ||
  filterDepto.value !== 'Todos' || filterPeriodo.value !== 'todo' ||
  filterDesde.value || filterHasta.value || sortBy.value !== 'reciente'
)

const limpiarFiltros = () => {
  searchQuery.value = ''
  filterEstado.value = 'Todos'
  filterTipo.value = 'Todos'
  filterDepto.value = 'Todos'
  filterPeriodo.value = 'todo'
  filterDesde.value = ''
  filterHasta.value = ''
  sortBy.value = 'reciente'
}

const bloqueosFiltrados = computed(() => {
  const hoy = startOfDay(new Date())

  let lista = bloqueos.value.filter(b => {
    if (filterEstado.value !== 'Todos' && b.estado !== filterEstado.value) return false
    if (filterTipo.value !== 'Todos' && b.tipo_evento !== filterTipo.value) return false
    if (filterDepto.value !== 'Todos' && b.departamento !== filterDepto.value) return false

    const q = searchQuery.value.toLowerCase()
    if (q && ![b.tipo_evento, b.municipio, b.departamento, b.direccion]
      .some(f => f?.toLowerCase().includes(q))) return false

    if (b.created_at && filterPeriodo.value !== 'todo') {
      const fecha = startOfDay(b.created_at)
      const diffDias = Math.round((hoy - fecha) / 86400000)
      if (filterPeriodo.value === 'hoy' && diffDias !== 0) return false
      if (filterPeriodo.value === 'ayer' && diffDias !== 1) return false
      if (filterPeriodo.value === 'semana' && diffDias > 6) return false
      if (filterPeriodo.value === 'mes' && diffDias > 29) return false
      if (filterPeriodo.value === 'custom') {
        if (filterDesde.value && fecha < startOfDay(filterDesde.value)) return false
        if (filterHasta.value && fecha > startOfDay(filterHasta.value)) return false
      }
    }
    return true
  })

  if (sortBy.value === 'reciente') lista = lista.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
  if (sortBy.value === 'antiguo') lista = lista.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0))
  if (sortBy.value === 'activos') lista = lista.sort((a, b) => a.estado === 'Activo' ? -1 : 1)

  return lista
})

// ─── Paginación de la tabla ─────────────────────────────────────────────
const PAGE_SIZE = 20
const currentPage = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(bloqueosFiltrados.value.length / PAGE_SIZE)))
const bloqueosPagina = computed(() => {
  const page = Math.min(currentPage.value, totalPages.value)
  return bloqueosFiltrados.value.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)
})
function goToPage(p) {
  currentPage.value = Math.max(1, Math.min(p, totalPages.value))
}
watch(bloqueosFiltrados, () => { currentPage.value = 1 })

const tiempoActualizado = computed(() => {
  if (!lastUpdated.value) return '—'
  const s = Math.floor((Date.now() - lastUpdated.value) / 1000)
  if (s < 10) return 'justo ahora'
  if (s < 60) return `hace ${s}s`
  return `hace ${Math.floor(s / 60)}m`
})

// ─── Animación de contadores ───────────────────────────────────────────
const animateCounters = () => {
  const targets = {
    total: bloqueos.value.length,
    activos: activos.value,
    finalizados: finalizados.value,
    tipos: Object.keys(tiposConteo.value).length,
  }
  const dur = 700
  const start = Date.now()
  const from = { ...displayCount.value }

  const tick = () => {
    const t = Math.min((Date.now() - start) / dur, 1)
    const ease = 1 - Math.pow(1 - t, 3)
    displayCount.value = {
      total: Math.round(from.total + (targets.total - from.total) * ease),
      activos: Math.round(from.activos + (targets.activos - from.activos) * ease),
      finalizados: Math.round(from.finalizados + (targets.finalizados - from.finalizados) * ease),
      tipos: Math.round(from.tipos + (targets.tipos - from.tipos) * ease),
    }
    if (t < 1) requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
}

// ─── Mapa ──────────────────────────────────────────────────────────────
const escapeHtml = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

const buildTooltipHtml = (b) => {
  const tipo = getTipo(b.tipo_evento)
  const activo = b.estado === 'Activo'
  return `
    <div style="min-width:180px;max-width:240px;">
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
        <span style="width:9px;height:9px;border-radius:50%;background:${tipo?.color || '#6b7280'};flex-shrink:0;"></span>
        <strong style="font-size:12.5px;color:#111827;">${escapeHtml(b.tipo_evento)}</strong>
        <span style="margin-left:auto;font-size:9.5px;font-weight:800;letter-spacing:.03em;padding:1px 6px;border-radius:9999px;background:${activo ? '#fee2e2' : '#dcfce7'};color:${activo ? '#dc2626' : '#16a34a'};">${b.estado.toUpperCase()}</span>
      </div>
      <div style="font-size:11.5px;color:#4b5563;line-height:1.3;">${escapeHtml(b.direccion)}</div>
      <div style="font-size:10.5px;color:#9ca3af;margin-top:1px;">${escapeHtml(b.municipio)}, ${escapeHtml(b.departamento)}</div>
      ${b.manifestantes_aproximados ? `<div style="font-size:10.5px;color:#6b7280;margin-top:3px;">👥 Aprox. ${escapeHtml(b.manifestantes_aproximados)} personas</div>` : ''}
    </div>
  `
}

const drawMarkers = () => {
  if (!markerLayer) return
  markerLayer.clearLayers()
  bloqueosFiltrados.value.forEach(b => {
    if (!b.latitud || !b.longitud) return
    const marker = L.marker([b.latitud, b.longitud], {
      icon: L.divIcon({
        className: '',
        html: buildMarkerHtml(b.tipo_evento, b.estado === 'Activo'),
        iconSize: [32, 32], iconAnchor: [16, 16],
      }),
    })
    marker.bindTooltip(() => buildTooltipHtml(b), {
      direction: 'top',
      offset: [0, -16],
      opacity: 1,
      className: 'event-tooltip',
    })
    marker.on('click', e => {
      L.DomEvent.stopPropagation(e)
      selectBloqueo(b)
      map.flyTo([b.latitud, b.longitud], 15, { animate: true, duration: 0.8 })
    })
    markerLayer.addLayer(marker)
  })
}

// Redibujar marcadores cada vez que cambia algún filtro
watch(bloqueosFiltrados, () => { drawMarkers() })

// ─── Fetch ─────────────────────────────────────────────────────────────
const showAlert = (bloqueo) => {
  clearTimeout(alertTimeout)
  newEventAlert.value = bloqueo
  alertTimeout = setTimeout(() => { newEventAlert.value = null }, 5000)
}

const fetchData = async (silent = false) => {
  try {
    ticking.value = true
    const prevIds = new Set(bloqueos.value.map(b => b.id))
    const res = await api.get('/api/bloqueos')
    if (silent) {
      const nuevos = res.data.filter(b => !prevIds.has(b.id))
      if (nuevos.length > 0) showAlert(nuevos[0])
    }
    bloqueos.value = res.data
    lastUpdated.value = Date.now()
    drawMarkers()
    animateCounters()
    setTimeout(() => { ticking.value = false }, 600)
  } catch (e) { ticking.value = false; console.error(e) }
}

// ─── Lifecycle ─────────────────────────────────────────────────────────
onMounted(async () => {
  document.title = 'Coyuntura SGIC — Situación en Tiempo Real'

  const isMobile = window.innerWidth < 640
  const initZoom = isMobile ? 9 : 7
  const initCenter = isMobile ? [14.64, -90.51] : GT_CENTER

  map = L.map(mapContainer.value, {
    maxBounds: GT_BOUNDS, maxBoundsViscosity: 1.0, minZoom: 6,
    zoomControl: false,
  }).setView(initCenter, initZoom)

  L.control.zoom({ position: 'bottomleft' }).addTo(map)

  const t = TILES[mapDark.value ? 'dark' : 'light']
  tileLayer = L.tileLayer(t.url, { attribution: t.attribution, maxZoom: 19 }).addTo(map)

  markerLayer = L.layerGroup().addTo(map)
  map.on('click', () => { deselectBloqueo() })

  await loadTipos()
  await fetchData()
  pollInterval = setInterval(() => fetchData(true), 20000)
  tickInterval = setInterval(() => { lastUpdated.value = lastUpdated.value }, 5000)
})

onUnmounted(() => {
  clearInterval(pollInterval)
  clearInterval(tickInterval)
  clearTimeout(alertTimeout)
  clearTimeout(selectedTimeout)
  map?.remove()
})

const focusMap = (b) => {
  map?.setView([b.latitud, b.longitud], 14)
  document.getElementById('hero-map')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  selectBloqueo(b)
}

const recenterMap = () => {
  if (!map) return
  const isMobile = window.innerWidth < 640
  const zoom = isMobile ? 9 : 7
  const center = isMobile ? [14.64, -90.51] : GT_CENTER
  deselectBloqueo()
  map.flyTo(center, zoom, { animate: true, duration: 1 })
}
</script>

<template>
  <div class="min-h-screen bg-slate-100 dark:bg-gray-950 text-gray-900 dark:text-white font-sans">

    <!-- ═══ HEADER ════════════════════════════════════════════════ -->
    <header class="fixed top-0 left-0 right-0 z-[2000] bg-white/90 dark:bg-gray-950/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
      <div class="max-w-[1400px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        <!-- Logo -->
        <div class="flex items-center gap-2.5">
          <img src="/logo-sgic.png" alt="Coyuntura SGIC" class="w-9 h-9 object-contain flex-shrink-0" />
          <div>
            <span class="font-black text-gray-900 dark:text-white text-base tracking-tight">Coyuntura SGIC</span>
            <span class="hidden sm:inline text-gray-400 dark:text-gray-500 text-xs ml-2">Guatemala</span>
          </div>
        </div>

        <!-- Indicador en vivo + nav -->
        <div class="flex items-center gap-2 sm:gap-4">
          <div class="hidden sm:flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-full px-3 py-1.5">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span class="text-xs text-gray-600 dark:text-gray-300 font-medium">En vivo · {{ tiempoActualizado }}</span>
          </div>

          <!-- Toggle mapa (tiles) -->
          <button @click="toggleTheme"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold border transition-all bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
            <svg v-if="mapDark" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
            </svg>
            <span class="hidden sm:inline">Mapa {{ mapDark ? 'Claro' : 'Oscuro' }}</span>
          </button>

          <!-- Toggle UI theme -->
          <button @click="toggleUITheme"
            class="p-1.5 rounded-full border transition-all bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
            :title="theme === 'dark' ? 'Modo claro' : 'Modo oscuro'">
            <svg v-if="theme === 'dark'" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
            </svg>
          </button>

          <!-- Ayuda -->
          <router-link to="/ayuda" title="Ayuda"
            class="p-1.5 rounded-full border transition-all bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"/>
            </svg>
          </router-link>

          <!-- Panel: solo editores -->
          <router-link v-if="auth.isEditor" to="/dashboard"
            class="text-xs font-semibold px-3 py-2 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition">
            Panel
          </router-link>
          <div class="flex items-center gap-2 pl-2 border-l border-gray-200 dark:border-gray-700">
            <div class="w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center text-xs font-black text-white">
              {{ auth.user?.name?.charAt(0).toUpperCase() }}
            </div>
            <span class="hidden sm:block text-xs text-gray-600 dark:text-gray-300 font-medium">{{ auth.user?.name }}</span>
            <button @click="logout"
              class="text-xs text-gray-400 dark:text-gray-500 hover:text-red-400 transition ml-1">
              Salir
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- ═══ HERO — MAPA ══════════════════════════════════════════ -->
    <section id="hero-map" class="relative pt-14 h-[52vh] sm:h-screen">

      <!-- Mapa ocupa toda la sección -->
      <div ref="mapContainer" class="absolute inset-0 top-14"></div>

      <!-- Alerta de nuevo evento -->
      <transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 -translate-y-3" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition duration-200" leave-to-class="opacity-0 -translate-y-3">
        <div v-if="newEventAlert"
          class="absolute top-20 left-1/2 -translate-x-1/2 z-[700] flex items-center gap-3 bg-red-600 text-white px-5 py-3 rounded-2xl shadow-2xl shadow-red-900/60 border border-red-500 cursor-pointer whitespace-nowrap"
          @click="newEventAlert = null">
          <span class="relative flex h-2.5 w-2.5 flex-shrink-0">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-white"></span>
          </span>
          <div>
            <p class="text-xs font-black uppercase tracking-wider">Nuevo evento registrado</p>
            <p class="text-xs opacity-90">{{ newEventAlert.tipo_evento }} · {{ newEventAlert.municipio }}, {{ newEventAlert.departamento }}</p>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 opacity-70 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
      </transition>

      <!-- Gradiente inferior (solo desktop) -->
      <div class="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-slate-100 dark:from-gray-950 to-transparent pointer-events-none z-[400] hidden sm:block"></div>

      <!-- Recentrar mapa -->
      <button @click="recenterMap" title="Centrar mapa"
        class="absolute bottom-24 left-4 z-[500] w-9 h-9 rounded-lg flex items-center justify-center bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 transition">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8a4 4 0 100 8 4 4 0 000-8z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 2v3m0 14v3M2 12h3m14 0h3"/>
        </svg>
      </button>

      <!-- Leyenda de tipos (top-right, solo md+) -->
      <div class="absolute top-20 right-4 z-[500] bg-white/90 dark:bg-gray-950/80 backdrop-blur rounded-xl p-3 border border-gray-200 dark:border-gray-700 hidden md:block">
        <p class="text-xs text-gray-500 dark:text-gray-400 font-semibold uppercase tracking-wider mb-2">Tipos</p>
        <div class="space-y-1.5">
          <div v-for="tipo in tipos" :key="tipo.nombre" class="flex items-center gap-2">
            <span class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
              :style="`background:${tipo.color}`">
              <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"
                viewBox="0 0 24 24" fill="none" stroke="white"
                stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
                v-html="tipo.iconPath">
              </svg>
            </span>
            <span class="text-xs text-gray-600 dark:text-gray-300">{{ tipo.nombre }}</span>
          </div>
        </div>
      </div>

      <!-- Stats flotantes en el bottom — solo desktop -->
      <div class="absolute bottom-8 left-0 right-0 z-[500] px-8 hidden sm:block pointer-events-none">
        <div class="max-w-[1400px] mx-auto grid grid-cols-4 gap-3 pointer-events-auto">
          <div class="bg-white/90 dark:bg-gray-900/90 backdrop-blur border border-gray-200 dark:border-gray-700 rounded-2xl p-4">
            <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Total</p>
            <p class="text-3xl font-black text-gray-900 dark:text-white">{{ displayCount.total }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">eventos registrados</p>
          </div>
          <div class="bg-white/90 dark:bg-gray-900/90 backdrop-blur border border-red-900/60 rounded-2xl p-4">
            <p class="text-xs text-red-400 uppercase tracking-wider font-semibold mb-1">Activos</p>
            <div class="flex items-end gap-2">
              <p class="text-3xl font-black text-red-400">{{ displayCount.activos }}</p>
              <p class="text-sm text-gray-400 dark:text-gray-500 mb-0.5" v-if="bloqueos.length">{{ Math.round(activos / bloqueos.length * 100) }}%</p>
            </div>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">en curso ahora</p>
          </div>
          <div class="bg-white/90 dark:bg-gray-900/90 backdrop-blur border border-green-900/60 rounded-2xl p-4">
            <p class="text-xs text-green-400 uppercase tracking-wider font-semibold mb-1">Inactivos</p>
            <div class="flex items-end gap-2">
              <p class="text-3xl font-black text-green-400">{{ displayCount.finalizados }}</p>
              <p class="text-sm text-gray-400 dark:text-gray-500 mb-0.5" v-if="bloqueos.length">{{ Math.round(finalizados / bloqueos.length * 100) }}%</p>
            </div>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">resueltos</p>
          </div>
          <div class="bg-white/90 dark:bg-gray-900/90 backdrop-blur border border-indigo-900/60 rounded-2xl p-4">
            <p class="text-xs text-indigo-400 uppercase tracking-wider font-semibold mb-1">Categorías</p>
            <p class="text-3xl font-black text-indigo-400">{{ displayCount.tipos }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">tipos distintos</p>
          </div>
        </div>
      </div>

      <!-- Tarjeta de evento seleccionado -->
      <transition
        enter-active-class="transition duration-250 ease-out"
        enter-from-class="opacity-0 translate-x-4"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-x-0"
        leave-to-class="opacity-0 translate-x-4"
      >
        <div v-if="selectedBloqueo"
          class="absolute top-24 right-4 z-[600] w-72 sm:w-80"
          @click.stop>
          <div @click="detailBloqueo = selectedBloqueo; clearTimeout(selectedTimeout)"
            class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl overflow-hidden cursor-pointer hover:ring-2 hover:ring-indigo-400 dark:hover:ring-indigo-500 transition">
            <!-- Franja de color del tipo -->
            <div class="h-1 w-full" :style="`background:${getTipo(selectedBloqueo.tipo_evento).color}`"></div>
            <div class="p-4">
              <div class="flex items-start justify-between mb-3">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    :style="`background:${getTipo(selectedBloqueo.tipo_evento).color}22`">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                      viewBox="0 0 24 24" fill="none" stroke-width="2.5"
                      stroke-linecap="round" stroke-linejoin="round"
                      :stroke="getTipo(selectedBloqueo.tipo_evento).color"
                      v-html="getTipo(selectedBloqueo.tipo_evento).iconPath">
                    </svg>
                  </div>
                  <div>
                    <h3 class="font-extrabold text-gray-900 dark:text-white text-sm uppercase tracking-wide">
                      {{ selectedBloqueo.tipo_evento }}
                    </h3>
                    <span class="text-xs font-bold px-2 py-0.5 rounded-full"
                      :class="selectedBloqueo.estado === 'Activo'
                        ? 'bg-red-900/50 text-red-400'
                        : 'bg-green-900/50 text-green-400'">
                      {{ selectedBloqueo.estado }}
                    </span>
                  </div>
                </div>
                <button @click.stop="deselectBloqueo()"
                  class="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
              <div class="space-y-2 text-sm">
                <div class="flex items-start gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.243-4.243a8 8 0 1111.314 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  <div>
                    <p class="text-gray-700 dark:text-gray-200 font-semibold">{{ selectedBloqueo.municipio }}, {{ selectedBloqueo.departamento }}</p>
                    <p class="text-gray-500 dark:text-gray-400 text-xs mt-0.5">{{ selectedBloqueo.direccion }}</p>
                  </div>
                </div>
                <div v-if="selectedBloqueo.manifestantes_aproximados" class="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  <span class="text-xs">Aprox. <strong class="text-gray-700 dark:text-gray-200">{{ selectedBloqueo.manifestantes_aproximados }}</strong> personas</span>
                </div>
                <!-- Foto -->
                <ImageCarousel v-if="(selectedBloqueo.fotos || []).length" :images="selectedBloqueo.fotos" height="140px" />
                <div v-else-if="selectedBloqueo.foto_path" class="rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700">
                  <img :src="selectedBloqueo.foto_path" alt="Fotografía del evento" class="w-full object-cover" style="max-height:140px;"/>
                </div>
                <!-- Observaciones -->
                <div v-if="selectedBloqueo.observaciones" class="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 border-l-2 border-gray-300 dark:border-gray-600 italic">
                  {{ selectedBloqueo.observaciones }}
                </div>
                <div class="pt-2 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between gap-1.5 text-gray-300 dark:text-gray-600 text-xs font-mono">
                  <span class="flex items-center gap-1.5">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                    </svg>
                    {{ selectedBloqueo.latitud }}, {{ selectedBloqueo.longitud }}
                  </span>
                  <span class="flex items-center gap-1 text-indigo-500 dark:text-indigo-400 font-sans font-semibold normal-case">
                    Ver detalles
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
                    </svg>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- Hint scroll -->
      <div class="absolute bottom-32 left-1/2 -translate-x-1/2 z-[500] animate-bounce pointer-events-none hidden sm:flex flex-col items-center gap-1">
        <span class="text-xs text-gray-400 dark:text-gray-500">Desplaza para más información</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-300 dark:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </div>
    </section>

    <!-- ═══ STATS MÓVIL (debajo del mapa, solo sm-) ══════════════ -->
    <div class="sm:hidden grid grid-cols-2 gap-3 px-4 py-4 bg-slate-100 dark:bg-gray-950">
      <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4">
        <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mb-1">Total</p>
        <p class="text-2xl font-black text-gray-900 dark:text-white">{{ displayCount.total }}</p>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">eventos registrados</p>
      </div>
      <div class="bg-white dark:bg-gray-900 border border-red-200 dark:border-red-900/60 rounded-2xl p-4">
        <p class="text-xs text-red-500 dark:text-red-400 uppercase tracking-wider font-semibold mb-1">Activos</p>
        <div class="flex items-end gap-2">
          <p class="text-2xl font-black text-red-500 dark:text-red-400">{{ displayCount.activos }}</p>
          <p class="text-xs text-gray-400 mb-0.5" v-if="bloqueos.length">{{ Math.round(activos / bloqueos.length * 100) }}%</p>
        </div>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">en curso ahora</p>
      </div>
      <div class="bg-white dark:bg-gray-900 border border-green-200 dark:border-green-900/60 rounded-2xl p-4">
        <p class="text-xs text-green-600 dark:text-green-400 uppercase tracking-wider font-semibold mb-1">Inactivos</p>
        <div class="flex items-end gap-2">
          <p class="text-2xl font-black text-green-600 dark:text-green-400">{{ displayCount.finalizados }}</p>
          <p class="text-xs text-gray-400 mb-0.5" v-if="bloqueos.length">{{ Math.round(finalizados / bloqueos.length * 100) }}%</p>
        </div>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">resueltos</p>
      </div>
      <div class="bg-white dark:bg-gray-900 border border-indigo-200 dark:border-indigo-900/60 rounded-2xl p-4">
        <p class="text-xs text-indigo-600 dark:text-indigo-400 uppercase tracking-wider font-semibold mb-1">Categorías</p>
        <p class="text-2xl font-black text-indigo-600 dark:text-indigo-400">{{ displayCount.tipos }}</p>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">tipos distintos</p>
      </div>
    </div>

    <!-- ═══ CONTENIDO ════════════════════════════════════════════ -->
    <div class="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">

      <!-- ── Estadísticas ────────────────────────────────────── -->
      <section>
        <div class="flex items-center gap-3 mb-6">
          <div class="w-1 h-6 bg-red-500 rounded-full"></div>
          <h2 class="text-xl font-extrabold text-gray-900 dark:text-white">Estadísticas</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-5 gap-5">

          <!-- Panel izquierdo: estado -->
          <div class="md:col-span-2 bg-white dark:bg-[#1C1C1E] rounded-2xl border border-[#E2E8F0] dark:border-[#2A2A2A] p-6">
            <p class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-5">Estado actual</p>

            <!-- Número grande -->
            <div class="mb-7">
              <p class="text-5xl font-black text-gray-900 dark:text-white leading-none">{{ bloqueos.length }}</p>
              <p class="text-sm text-gray-400 dark:text-gray-500 mt-1.5">eventos registrados en total</p>
            </div>

            <!-- Activos -->
            <div class="mb-4">
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-red-500 flex-shrink-0"></span>
                  <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">Activos</span>
                </div>
                <div class="flex items-baseline gap-2">
                  <span class="text-base font-black text-red-500">{{ activos }}</span>
                  <span class="text-xs text-gray-400 dark:text-gray-500" v-if="bloqueos.length">{{ Math.round(activos / bloqueos.length * 100) }}%</span>
                </div>
              </div>
              <div class="h-2 bg-gray-100 dark:bg-[#2A2A2A] rounded-full overflow-hidden">
                <div class="h-full bg-red-500 rounded-full transition-all duration-700"
                  :style="`width:${bloqueos.length ? Math.round(activos / bloqueos.length * 100) : 0}%`"></div>
              </div>
            </div>

            <!-- Inactivos -->
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 flex-shrink-0"></span>
                  <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">Inactivos</span>
                </div>
                <div class="flex items-baseline gap-2">
                  <span class="text-base font-black text-emerald-500">{{ finalizados }}</span>
                  <span class="text-xs text-gray-400 dark:text-gray-500" v-if="bloqueos.length">{{ Math.round(finalizados / bloqueos.length * 100) }}%</span>
                </div>
              </div>
              <div class="h-2 bg-gray-100 dark:bg-[#2A2A2A] rounded-full overflow-hidden">
                <div class="h-full bg-emerald-500 rounded-full transition-all duration-700"
                  :style="`width:${bloqueos.length ? Math.round(finalizados / bloqueos.length * 100) : 0}%`"></div>
              </div>
            </div>
          </div>

          <!-- Panel derecho: por tipo -->
          <div class="md:col-span-3 bg-white dark:bg-[#1C1C1E] rounded-2xl border border-[#E2E8F0] dark:border-[#2A2A2A] p-6">
            <p class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-5">Eventos por tipo</p>

            <div v-if="!Object.keys(tiposConteo).length"
              class="flex items-center justify-center h-32 text-gray-300 dark:text-gray-600 text-sm">
              Sin datos
            </div>

            <div v-else class="space-y-4">
              <div v-for="tipo in tipos.filter(t => tiposConteo[t.nombre])" :key="tipo.nombre">
                <div class="flex items-center justify-between mb-1.5">
                  <div class="flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                      :style="`background:${tipo.color}18`">
                      <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13"
                        viewBox="0 0 24 24" fill="none" stroke-width="2.5"
                        stroke-linecap="round" stroke-linejoin="round"
                        :stroke="tipo.color" v-html="tipo.iconPath"/>
                    </div>
                    <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ tipo.nombre }}</span>
                  </div>
                  <div class="flex items-baseline gap-2">
                    <span class="text-base font-black" :style="`color:${tipo.color}`">{{ tiposConteo[tipo.nombre] }}</span>
                    <span class="text-xs text-gray-400 dark:text-gray-500 w-8 text-right" v-if="bloqueos.length">
                      {{ Math.round(tiposConteo[tipo.nombre] / bloqueos.length * 100) }}%
                    </span>
                  </div>
                </div>
                <div class="h-1.5 bg-gray-100 dark:bg-[#2A2A2A] rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-700"
                    :style="`width:${bloqueos.length ? Math.round(tiposConteo[tipo.nombre] / bloqueos.length * 100) : 0}%; background:${tipo.color}`"></div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- ── Listado de eventos ────────────────────────────────── -->
      <section>
        <div class="flex items-center gap-3 mb-6">
          <div class="w-1 h-6 bg-indigo-500 rounded-full"></div>
          <h2 class="text-xl font-extrabold text-gray-900 dark:text-white">Eventos Reportados</h2>
          <span class="text-sm text-gray-400 dark:text-gray-500 font-medium">
            ({{ bloqueosFiltrados.length }} de {{ bloqueos.length }})
          </span>
        </div>

        <!-- Filtros -->
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 mb-5 space-y-3">

          <!-- Fila 1: búsqueda + limpiar -->
          <div class="flex gap-3 items-center">
            <div class="relative flex-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              <input v-model="searchQuery" type="text" placeholder="Buscar por lugar, tipo, dirección..."
                class="w-full bg-gray-50 border border-gray-200 dark:bg-gray-800 dark:border-gray-700 rounded-xl pl-9 pr-4 py-2 text-sm text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"/>
            </div>
            <transition enter-active-class="transition duration-150" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100">
              <button v-if="hayFiltrosActivos" @click="limpiarFiltros"
                class="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 hover:bg-red-100 dark:hover:bg-red-900/40 transition whitespace-nowrap">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
                Limpiar
              </button>
            </transition>
          </div>

          <!-- Fila 2: período rápido -->
          <div class="flex flex-wrap gap-2 items-center">
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500 mr-1">Período:</span>
            <button v-for="p in [
              { key:'hoy',    label:'Hoy' },
              { key:'ayer',   label:'Ayer' },
              { key:'semana', label:'Últ. 7 días' },
              { key:'mes',    label:'Últ. 30 días' },
              { key:'todo',   label:'Todo' },
              { key:'custom', label:'Personalizado' },
            ]" :key="p.key" @click="filterPeriodo = p.key"
              class="px-3 py-1.5 rounded-full text-xs font-semibold border transition"
              :class="filterPeriodo === p.key
                ? 'bg-indigo-600 border-indigo-500 text-white shadow-sm'
                : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:border-indigo-400 hover:text-indigo-500'">
              {{ p.label }}
            </button>
          </div>

          <!-- Fila 2b: rango personalizado (solo si custom) -->
          <transition enter-active-class="transition duration-200" enter-from-class="opacity-0 -translate-y-1" enter-to-class="opacity-100 translate-y-0">
            <div v-if="filterPeriodo === 'custom'" class="flex flex-wrap gap-3 items-center pl-1">
              <div class="flex items-center gap-2">
                <label class="text-xs text-gray-400 dark:text-gray-500 font-semibold">Desde</label>
                <input type="date" v-model="filterDesde"
                  class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 text-xs text-gray-700 dark:text-gray-300 focus:outline-none focus:border-indigo-500 transition"/>
              </div>
              <div class="flex items-center gap-2">
                <label class="text-xs text-gray-400 dark:text-gray-500 font-semibold">Hasta</label>
                <input type="date" v-model="filterHasta"
                  class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 text-xs text-gray-700 dark:text-gray-300 focus:outline-none focus:border-indigo-500 transition"/>
              </div>
            </div>
          </transition>

          <!-- Fila 3: estado, tipo, departamento, ordenar -->
          <div class="flex flex-wrap gap-2 items-center border-t border-gray-100 dark:border-gray-800 pt-3">
            <!-- Estado -->
            <div class="flex rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden text-xs font-semibold">
              <button v-for="opt in ['Todos','Activo','Inactivo']" :key="opt"
                @click="filterEstado = opt"
                class="px-3 py-1.5 transition"
                :class="filterEstado === opt
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-700 dark:hover:text-gray-300'">
                {{ opt }}
              </button>
            </div>

            <!-- Tipo -->
            <select v-model="filterTipo"
              class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-1.5 text-xs text-gray-600 dark:text-gray-300 focus:outline-none focus:border-indigo-500 transition">
              <option value="Todos">Todos los tipos</option>
              <option v-for="t in tipos" :key="t.nombre" :value="t.nombre">{{ t.nombre }}</option>
            </select>

            <!-- Departamento -->
            <select v-model="filterDepto"
              class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-1.5 text-xs text-gray-600 dark:text-gray-300 focus:outline-none focus:border-indigo-500 transition">
              <option v-for="d in deptosDisponibles" :key="d" :value="d">
                {{ d === 'Todos' ? 'Todos los dptos.' : d }}
              </option>
            </select>

            <!-- Ordenar -->
            <div class="ml-auto flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/>
              </svg>
              <select v-model="sortBy"
                class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-1.5 text-xs text-gray-600 dark:text-gray-300 focus:outline-none focus:border-indigo-500 transition">
                <option value="reciente">Más reciente</option>
                <option value="antiguo">Más antiguo</option>
                <option value="activos">Activos primero</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Resumen de filtros activos -->
        <div v-if="hayFiltrosActivos" class="flex items-center gap-2 mb-4 text-xs text-gray-400 dark:text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-.293.707L13 13.414V19a1 1 0 01-.553.894l-4 2A1 1 0 017 21v-7.586L3.293 6.707A1 1 0 013 6V4z"/>
          </svg>
          Mostrando <strong class="text-indigo-500">{{ bloqueosFiltrados.length }}</strong> de {{ bloqueos.length }} eventos con filtros aplicados
        </div>

        <!-- Tabla de eventos -->
        <div v-if="bloqueosFiltrados.length > 0"
          class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-[#E2E8F0] dark:border-[#2A2A2A] bg-gray-50 dark:bg-[#161616]">
                  <th class="text-left px-4 py-2.5 font-mono text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500">Estado</th>
                  <th class="text-left px-4 py-2.5 font-mono text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500">Tipo</th>
                  <th class="text-left px-4 py-2.5 font-mono text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500">Ubicación</th>
                  <th class="text-left px-4 py-2.5 font-mono text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500 hidden md:table-cell">Dirección</th>
                  <th class="text-right px-4 py-2.5 font-mono text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500 hidden sm:table-cell">Personas</th>
                  <th class="text-right px-4 py-2.5 font-mono text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500">Hace</th>
                  <th class="px-4 py-2.5"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in bloqueosPagina" :key="b.id"
                  @click="detailBloqueo = b"
                  class="group border-b border-[#F0F0F0] dark:border-[#252525] last:border-b-0 cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-[#242424]">
                  <td class="px-4 py-2.5">
                    <span class="inline-flex items-center gap-1.5 text-xs font-bold px-2 py-0.5 rounded-full border"
                      :class="b.estado === 'Activo'
                        ? 'bg-red-50 text-red-600 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800/40'
                        : 'bg-gray-100 text-gray-500 border-gray-200 dark:bg-[#252525] dark:text-gray-400 dark:border-[#3A3A3A]'">
                      <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :style="`background:${b.estado === 'Activo' ? '#dc2626' : '#9ca3af'}`"></span>
                      {{ b.estado }}
                    </span>
                  </td>
                  <td class="px-4 py-2.5">
                    <div class="flex items-center gap-2 min-w-0">
                      <span class="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0" :style="`background:${getTipo(b.tipo_evento).color}18`">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke-width="2.5"
                          stroke-linecap="round" stroke-linejoin="round" :stroke="getTipo(b.tipo_evento).color" v-html="getTipo(b.tipo_evento).iconPath"/>
                      </span>
                      <span class="font-semibold text-gray-800 dark:text-gray-200 truncate">{{ b.tipo_evento }}</span>
                    </div>
                  </td>
                  <td class="px-4 py-2.5 text-gray-600 dark:text-gray-300 whitespace-nowrap">{{ b.municipio }}, {{ b.departamento }}</td>
                  <td class="px-4 py-2.5 text-gray-400 dark:text-gray-500 max-w-[260px] truncate hidden md:table-cell">{{ b.direccion }}</td>
                  <td class="px-4 py-2.5 text-right text-gray-500 dark:text-gray-400 hidden sm:table-cell">{{ b.manifestantes_aproximados ? `~${b.manifestantes_aproximados}` : '—' }}</td>
                  <td class="px-4 py-2.5 text-right text-gray-400 dark:text-gray-500 whitespace-nowrap" :title="formatFechaCorta(b.created_at)">{{ formatFechaRelativa(b.created_at) }}</td>
                  <td class="px-4 py-2.5 text-right">
                    <button @click.stop="focusMap(b)" title="Ver en mapa"
                      class="p-1.5 rounded-lg text-gray-300 dark:text-gray-600 group-hover:text-indigo-500 dark:group-hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex items-center gap-1 px-4 py-3 border-t border-[#E2E8F0] dark:border-[#2A2A2A] flex-wrap">
            <button class="w-8 h-8 flex items-center justify-center rounded-lg border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 text-xs font-bold disabled:opacity-35 hover:border-indigo-400 hover:text-indigo-500 transition"
              :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)" type="button">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5"/></svg>
            </button>
            <template v-for="p in totalPages" :key="p">
              <button v-if="p === 1 || p === totalPages || Math.abs(p - currentPage) <= 1"
                class="min-w-8 h-8 px-1 flex items-center justify-center rounded-lg border text-xs font-bold transition"
                :class="p === currentPage
                  ? 'bg-indigo-600 border-indigo-600 text-white'
                  : 'border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 hover:border-indigo-400 hover:text-indigo-500'"
                @click="goToPage(p)" type="button">{{ p }}</button>
              <span v-else-if="p === currentPage - 2 || p === currentPage + 2" class="text-xs text-gray-400 px-0.5">…</span>
            </template>
            <button class="w-8 h-8 flex items-center justify-center rounded-lg border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 text-xs font-bold disabled:opacity-35 hover:border-indigo-400 hover:text-indigo-500 transition"
              :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)" type="button">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/></svg>
            </button>
            <span class="ml-auto text-xs font-mono text-gray-400 dark:text-gray-500 whitespace-nowrap">
              {{ (currentPage - 1) * PAGE_SIZE + 1 }}–{{ Math.min(currentPage * PAGE_SIZE, bloqueosFiltrados.length) }} de {{ bloqueosFiltrados.length }}
            </span>
          </div>
        </div>

        <!-- Empty state -->
        <div v-else class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl py-16 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-gray-200 dark:text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <p class="text-gray-400 dark:text-gray-500 text-sm font-medium">No hay eventos en ese período</p>
          <button @click="limpiarFiltros"
            class="mt-3 text-xs text-indigo-500 dark:text-indigo-400 hover:underline transition">
            Limpiar filtros
          </button>
        </div>
      </section>
    </div>

    <!-- ═══ FOOTER ════════════════════════════════════════════════ -->
    <AppFooter :status="`Actualización automática · ${tiempoActualizado}`" />

    <!-- Modal de detalles completos -->
    <EventDetailModal v-if="detailBloqueo" :bloqueo="detailBloqueo" @close="detailBloqueo = null" />

  </div>
</template>

<style>
.leaflet-top, .leaflet-bottom { z-index: 450 !important; }
.leaflet-control-zoom a {
  background: #1f2937 !important;
  color: #d1d5db !important;
  border-color: #374151 !important;
}
.leaflet-control-zoom a:hover {
  background: #374151 !important;
  color: #fff !important;
}
.leaflet-control-attribution {
  background: rgba(0,0,0,0.5) !important;
  color: #6b7280 !important;
  font-size: 10px !important;
}
.event-tooltip {
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 10px !important;
  padding: 8px 10px !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.18) !important;
  opacity: 1 !important;
  white-space: normal !important;
  max-width: 240px;
}
.event-tooltip::before {
  border-top-color: #ffffff !important;
}
</style>
