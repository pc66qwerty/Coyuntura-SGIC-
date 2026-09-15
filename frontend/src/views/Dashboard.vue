<template>
  <div class="dashboard-page">
    <header class="dash-header">
      <div class="header-main">
        <router-link to="/" class="back-link" aria-label="Volver al mapa principal">
          <svg class="icon" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
        </router-link>

        <div class="title-block">
          <p>Monitor Vial</p>
          <h1>Panel de control</h1>
          <span>Actualizado: {{ lastUpdate || 'pendiente' }}</span>
        </div>

        <div v-if="newEventsCount > 0" class="live-badge">
          <span></span>
          {{ newEventsCount }} nuevos
        </div>
      </div>

      <nav class="header-actions" aria-label="Acciones del panel">
        <div class="theme-switch" aria-label="Tema visual">
          <button type="button" :class="{ active: theme === 'light' }" @click="applyTheme('light')">
            Claro
          </button>
          <button type="button" :class="{ active: theme === 'dark' }" @click="applyTheme('dark')">
            Oscuro
          </button>
        </div>
        <button @click="exportCSV" class="tool-btn" type="button">
          <svg class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          CSV
        </button>
        <button @click="print" :disabled="printLoading" class="tool-btn" type="button">
          <svg v-if="!printLoading" class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6.72 13.829c-.24.03-.48.062-.72.096m.72-.096a42.415 42.415 0 0 1 10.56 0m-10.56 0L6.34 18m10.94-4.171c.24.03.48.062.72.096m-.72-.096L17.66 18M6.34 18H5.25A2.25 2.25 0 0 1 3 15.75V9.456c0-1.081.768-2.015 1.837-2.175a48.041 48.041 0 0 1 1.913-.247m10.5 0a48.536 48.536 0 0 0-10.5 0m10.5 0c.648.05 1.287.133 1.913.247C20.232 7.441 21 8.375 21 9.456v6.294A2.25 2.25 0 0 1 18.75 18h-1.09" />
          </svg>
          <svg v-else class="icon-sm spinner" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          {{ printLoading ? 'Generando' : 'PDF' }}
        </button>
        <router-link to="/usuarios" class="tool-btn">Usuarios</router-link>
        <router-link to="/tipos-evento" class="tool-btn">Tipos</router-link>
      </nav>
    </header>

    <main class="dashboard-shell">
      <section class="overview-grid" aria-label="Resumen operativo">
        <article class="metric-card metric-total">
          <span>Total eventos</span>
          <strong>{{ bloqueos.length }}</strong>
          <small>Registros en sistema</small>
        </article>
        <article class="metric-card metric-danger">
          <span>Activos</span>
          <strong>{{ activos }}</strong>
          <small>{{ bloqueos.length ? Math.round(activos / bloqueos.length * 100) : 0 }}% del total</small>
        </article>
        <article class="metric-card metric-success">
          <span>Finalizados</span>
          <strong>{{ finalizados }}</strong>
          <small>{{ bloqueos.length ? Math.round(finalizados / bloqueos.length * 100) : 0 }}% del total</small>
        </article>
        <article class="distribution-card">
          <div class="card-heading">
            <span>Tipos principales</span>
          </div>
          <div v-if="Object.keys(tipoStats).length" class="type-list">
            <div v-for="(count, tipo) in tipoStats" :key="tipo" class="type-row">
              <i :style="{ background: getTipoColor(tipo) }"></i>
              <span>{{ tipo }}</span>
              <strong>{{ count }}</strong>
            </div>
          </div>
          <p v-else class="empty-note">Sin datos disponibles</p>
        </article>
      </section>

      <section class="work-grid">
        <aside class="control-stack">
          <section class="panel register-panel">
            <button @click="showForm = !showForm" class="panel-toggle" type="button">
              <span>
                <small>Registro</small>
                <strong>Nuevo evento vial</strong>
              </span>
              <svg class="icon-sm" :class="{ rotated: showForm }" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
            <div v-if="showForm" class="form-region">
              <BloqueoForm
                :pending-coords="pendingCoords"
                :pick-mode="pickMode"
                @created="onCreated"
                @toggle-pick-mode="pickMode = !pickMode"
                @focus-location="adminMapRef?.focusOn($event.lat, $event.lng, $event.zoom)"
              />
            </div>
          </section>

          <section class="panel list-panel">
            <div class="card-heading">
              <span>Eventos</span>
              <strong>{{ filteredList.length }}</strong>
            </div>

            <div class="filter-box">
              <label class="search-field">
                <svg class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607z" />
                </svg>
                <input v-model="listSearch" placeholder="Buscar por tipo, municipio o direccion" />
              </label>

              <div class="segmented">
                <button
                  v-for="s in ['Todos', 'Activo', 'Finalizado']"
                  :key="s"
                  @click="listEstado = s"
                  :class="{ active: listEstado === s }"
                  type="button"
                >
                  {{ s }}
                </button>
              </div>

              <div class="date-row">
                <input v-model="dateFrom" type="date" aria-label="Fecha inicial" />
                <input v-model="dateTo" type="date" aria-label="Fecha final" />
              </div>
            </div>

            <BloqueoList
              :bloqueos="pagedList"
              :can-edit="true"
              @status-changed="onStatusChanged"
              @focus-event="onFocusEvent"
              @edit-event="editingBloqueo = $event"
              @deleted="onDeleted"
            />

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="pagination">
              <button class="pg-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)" type="button">
                <svg class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5"/></svg>
              </button>
              <template v-for="p in totalPages" :key="p">
                <button
                  v-if="p === 1 || p === totalPages || Math.abs(p - currentPage) <= 1"
                  class="pg-btn" :class="{ 'pg-active': p === currentPage }"
                  @click="goToPage(p)" type="button">{{ p }}</button>
                <span v-else-if="p === currentPage - 2 || p === currentPage + 2" class="pg-ellipsis">…</span>
              </template>
              <button class="pg-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)" type="button">
                <svg class="icon-sm" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/></svg>
              </button>
              <span class="pg-info">{{ (currentPage - 1) * PAGE_SIZE + 1 }}–{{ Math.min(currentPage * PAGE_SIZE, filteredList.length) }} de {{ filteredList.length }}</span>
            </div>
          </section>
        </aside>

        <section class="map-stack">
          <div class="panel map-panel">
            <div class="map-header">
              <div>
                <span>Mapa administrativo</span>
                <small>Vista de eventos y seleccion de coordenadas</small>
              </div>
              <button v-if="showForm" @click="pickMode = !pickMode" class="pick-btn" :class="{ active: pickMode }" type="button">
                {{ pickMode ? 'Seleccionando' : 'Elegir punto' }}
              </button>
            </div>
            <div class="map-body">
              <AdminMap
                ref="adminMapRef"
                :bloqueos="bloqueos"
                :pick-mode="pickMode"
                @coords-selected="onCoordsSelected"
              />
            </div>
          </div>

          <div class="panel depto-panel">
            <div class="card-heading">
              <span>Departamentos activos</span>
            </div>
            <div v-if="topDeptos.length" class="depto-list">
              <div v-for="(item, i) in topDeptos" :key="item.nombre" class="depto-row">
                <span>{{ i + 1 }}</span>
                <strong>{{ item.nombre }}</strong>
                <div>
                  <i :style="{ width: (item.count / (topDeptos[0]?.count || 1) * 100) + '%' }"></i>
                </div>
                <em>{{ item.count }}</em>
              </div>
            </div>
            <p v-else class="empty-note">Sin eventos activos por departamento</p>
          </div>
        </section>
      </section>
    </main>

    <!-- Credits footer -->
    <footer class="credits-footer">
      <span class="credits-label">Desarrollado por</span>
      <div class="credits-orgs">
        <div class="credits-org">
          <img src="/SESIC.png" alt="SESIC" class="credits-logo" />
          <span>Sección de Sistemas de Información Criminal</span>
        </div>
        <div class="credits-divider"></div>
        <div class="credits-org">
          <img src="/CRADIC.png" alt="CRADIC" class="credits-logo" />
          <span>CRADIC</span>
        </div>
        <div class="credits-divider"></div>
        <div class="credits-org">
          <img src="/SGIC.png" alt="SGIC" class="credits-logo" />
          <span>SGIC</span>
        </div>
      </div>
    </footer>

    <div class="toast-area">
      <transition-group name="toast">
        <div v-for="toast in toasts" :key="toast.id" class="toast" :class="`toast-${toast.type}`">
          {{ toast.message }}
        </div>
      </transition-group>
    </div>

    <BloqueoEditModal
      v-if="editingBloqueo"
      :bloqueo="editingBloqueo"
      @updated="onUpdated"
      @close="editingBloqueo = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import AdminMap from '@/components/AdminMap.vue'
import BloqueoForm from '@/components/BloqueoForm.vue'
import BloqueoList from '@/components/BloqueoList.vue'
import BloqueoEditModal from '@/components/BloqueoEditModal.vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import { useTheme } from '@/composables/useTheme'
import api from '@/api'

const { load: loadTipos, getTipo } = useTiposEvento()
const { theme, apply: applyTheme } = useTheme()

const bloqueos = ref([])
const showForm = ref(false)
const pickMode = ref(false)
const pendingCoords = ref(null)
const editingBloqueo = ref(null)
const adminMapRef = ref(null)
const newEventsCount = ref(0)
const toasts = ref([])
const lastUpdate = ref('')
const listSearch = ref('')
const listEstado = ref('Todos')
const dateFrom = ref('')
const dateTo = ref('')
const printLoading = ref(false)
const currentPage = ref(1)
const PAGE_SIZE = 10

let pollInterval = null
let toastId = 0

function getTipoColor(nombre) {
  return getTipo(nombre)?.color || '#6b7280'
}

const activos = computed(() => bloqueos.value.filter((b) => b.estado === 'Activo').length)
const finalizados = computed(() => bloqueos.value.filter((b) => b.estado === 'Finalizado').length)

const tipoStats = computed(() => {
  const stats = {}
  bloqueos.value.forEach((b) => {
    stats[b.tipo_evento] = (stats[b.tipo_evento] || 0) + 1
  })
  return Object.fromEntries(Object.entries(stats).sort((a, b) => b[1] - a[1]).slice(0, 5))
})

const topDeptos = computed(() => {
  const stats = {}
  bloqueos.value.filter((b) => b.estado === 'Activo').forEach((b) => {
    stats[b.departamento] = (stats[b.departamento] || 0) + 1
  })
  return Object.entries(stats)
    .map(([nombre, count]) => ({ nombre, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
})

const filteredList = computed(() => {
  let list = [...bloqueos.value]
  if (listSearch.value) {
    const q = listSearch.value.toLowerCase()
    list = list.filter((b) =>
      [b.tipo_evento, b.municipio, b.departamento, b.direccion].some((v) => v?.toLowerCase().includes(q))
    )
  }
  if (listEstado.value !== 'Todos') list = list.filter((b) => b.estado === listEstado.value)
  if (dateFrom.value) list = list.filter((b) => new Date(b.created_at) >= new Date(dateFrom.value))
  if (dateTo.value) list = list.filter((b) => new Date(b.created_at) <= new Date(`${dateTo.value}T23:59:59`))
  return list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredList.value.length / PAGE_SIZE)))

const pagedList = computed(() => {
  const page = Math.min(currentPage.value, totalPages.value)
  return filteredList.value.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)
})

function goToPage(p) {
  currentPage.value = Math.max(1, Math.min(p, totalPages.value))
}

watch([listSearch, listEstado, dateFrom, dateTo], () => { currentPage.value = 1 })

function showToast(message, type = 'success') {
  const id = ++toastId
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }, 4000)
}

async function fetchBloqueos() {
  try {
    const { data } = await api.get('/api/bloqueos')
    const prev = bloqueos.value.length
    if (prev > 0 && data.length > prev) {
      const diff = data.length - prev
      newEventsCount.value += diff
      showToast(`${diff} nuevo${diff > 1 ? 's' : ''} evento${diff > 1 ? 's' : ''} registrado${diff > 1 ? 's' : ''}`, 'info')
    }
    bloqueos.value = data
    lastUpdate.value = new Date().toLocaleTimeString('es-GT')
  } catch {
    showToast('No se pudieron cargar los eventos', 'warning')
  }
}

function onCoordsSelected(coords) {
  pendingCoords.value = coords
}

function onCreated(bloqueo) {
  bloqueos.value.unshift(bloqueo)
  pickMode.value = false
  pendingCoords.value = null
  adminMapRef.value?.clearTempMarker()
  showForm.value = false
  showToast('Evento registrado correctamente', 'success')
}

function onStatusChanged(updated) {
  const idx = bloqueos.value.findIndex((b) => b.id === updated.id)
  if (idx !== -1) bloqueos.value[idx] = updated
}

function onFocusEvent(b) {
  adminMapRef.value?.focusOn(b.latitud, b.longitud)
}

function onUpdated(updated) {
  const idx = bloqueos.value.findIndex((b) => b.id === updated.id)
  if (idx !== -1) bloqueos.value[idx] = updated
  editingBloqueo.value = null
  showToast('Evento actualizado', 'success')
}

function onDeleted(id) {
  bloqueos.value = bloqueos.value.filter((b) => b.id !== id)
  showToast('Evento eliminado', 'warning')
}

function exportCSV() {
  const cols = ['ID', 'Tipo', 'Direccion', 'Municipio', 'Departamento', 'Estado', 'Personas', 'Latitud', 'Longitud', 'Creado']
  const rows = bloqueos.value.map((b) => [
    b.id,
    b.tipo_evento,
    b.direccion,
    b.municipio,
    b.departamento,
    b.estado,
    b.manifestantes_aproximados || '',
    b.latitud,
    b.longitud,
    b.created_at,
  ])
  const csv = [cols, ...rows].map((r) => r.map((v) => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `monitor-vial-${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

function print() {
  if (printLoading.value) return
  printLoading.value = true
  try {
    const list = filteredList.value
    const rows = list.map((b) => `
      <tr>
        <td>${b.id}</td>
        <td>${b.tipo_evento}</td>
        <td>${b.municipio}, ${b.departamento}</td>
        <td>${b.direccion || ''}</td>
        <td>${b.estado}</td>
        <td>${new Date(b.created_at).toLocaleString('es-GT')}</td>
      </tr>
    `).join('')
    const win = window.open('', '_blank')
    if (!win) return
    win.document.write(`<!DOCTYPE html>
      <html lang="es">
        <head>
          <meta charset="UTF-8" />
          <title>Reporte Monitor Vial</title>
          <style>
            body{font-family:Arial,sans-serif;color:#17202a;margin:28px}
            h1{margin:0 0 4px;font-size:24px}
            p{margin:0 0 18px;color:#66707c}
            table{width:100%;border-collapse:collapse;font-size:12px}
            th{background:#1e3a5f;color:#fff;text-align:left;padding:8px}
            td{border-bottom:1px solid #d8d2c4;padding:7px}
            .stats{display:flex;gap:10px;margin:18px 0}
            .stat{border:1px solid #d8d2c4;padding:10px 14px;border-radius:8px}
            .stat strong{display:block;font-size:22px}
          </style>
        </head>
        <body>
          <h1>Reporte Monitor Vial</h1>
          <p>Generado: ${new Date().toLocaleString('es-GT')}</p>
          <div class="stats">
            <div class="stat"><span>Total</span><strong>${list.length}</strong></div>
            <div class="stat"><span>Activos</span><strong>${list.filter((b) => b.estado === 'Activo').length}</strong></div>
            <div class="stat"><span>Finalizados</span><strong>${list.filter((b) => b.estado === 'Finalizado').length}</strong></div>
          </div>
          <table>
            <thead>
              <tr><th>ID</th><th>Tipo</th><th>Ubicacion</th><th>Direccion</th><th>Estado</th><th>Creado</th></tr>
            </thead>
            <tbody>${rows || '<tr><td colspan="6">Sin eventos</td></tr>'}</tbody>
          </table>
          <script>window.onload=()=>setTimeout(()=>window.print(),300)<\/script>
        </body>
      </html>`)
    win.document.close()
  } finally {
    printLoading.value = false
  }
}

onMounted(async () => {
  await loadTipos()
  await fetchBloqueos()
  pollInterval = setInterval(fetchBloqueos, 30000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--bg);
  color: var(--t1);
}

.dash-header {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 28px;
  border-bottom: 1px solid var(--border);
  background: color-mix(in srgb, var(--surface) 94%, transparent);
  backdrop-filter: blur(14px);
}

.header-main,
.header-actions,
.tool-btn,
.back-link,
.live-badge {
  display: flex;
  align-items: center;
}

.header-main {
  gap: 14px;
  min-width: 0;
}

.back-link {
  width: 38px;
  height: 38px;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--t2);
  background: var(--bg);
}

.back-link:hover,
.tool-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.title-block p {
  margin: 0 0 2px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--accent);
}

.title-block h1 {
  margin: 0;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 30px;
  line-height: 1;
  color: var(--t1);
}

.title-block span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--t3);
}

.live-badge {
  gap: 7px;
  padding: 6px 10px;
  border: 1px solid var(--accent);
  border-radius: 999px;
  color: var(--accent);
  background: var(--accent-dim);
  font-size: 12px;
  font-weight: 700;
}

.live-badge span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
}

.header-actions {
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.theme-switch {
  display: inline-grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  min-height: 36px;
  padding: 4px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
}

.theme-switch button {
  min-width: 58px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--t2);
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.theme-switch button.active {
  background: var(--surface);
  color: var(--t1);
  box-shadow: inset 0 0 0 1px var(--border);
}

.theme-switch button:hover {
  color: var(--accent);
}

.tool-btn {
  min-height: 36px;
  gap: 7px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--t2);
  font-size: 12px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
}

.tool-btn:disabled {
  cursor: wait;
  opacity: 0.58;
}

.dashboard-shell {
  width: min(1480px, 100%);
  margin: 0 auto;
  padding: 24px 28px 34px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(150px, 1fr)) minmax(260px, 1.15fr);
  gap: 14px;
  margin-bottom: 18px;
}

.metric-card,
.distribution-card,
.panel {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
}

.metric-card {
  min-height: 126px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.metric-card span,
.card-heading span,
.panel-toggle small,
.map-header small {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--t3);
}

.metric-card strong {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 48px;
  line-height: 0.9;
  color: var(--t1);
}

.metric-card small {
  color: var(--t2);
  font-size: 12px;
}

.metric-danger strong {
  color: #dc2626;
}

.metric-success strong {
  color: #16a34a;
}

.distribution-card {
  padding: 16px;
}

.card-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.card-heading strong {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 28px;
  color: var(--t1);
}

.type-list,
.depto-list {
  display: grid;
  gap: 9px;
}

.type-row,
.depto-row {
  display: grid;
  align-items: center;
  gap: 9px;
  color: var(--t2);
  font-size: 13px;
}

.type-row {
  grid-template-columns: 9px minmax(0, 1fr) auto;
}

.type-row i {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.type-row span,
.depto-row strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-row strong,
.depto-row em {
  color: var(--t1);
  font-style: normal;
  font-weight: 800;
}

.work-grid {
  display: grid;
  grid-template-columns: minmax(420px, 0.44fr) minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.control-stack {
  display: grid;
  gap: 18px;
}

.map-stack {
  display: grid;
  gap: 18px;
  position: sticky;
  top: 92px;
  align-self: start;
}

.panel {
  overflow: hidden;
}

.panel-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px;
  border: 0;
  background: transparent;
  color: var(--t1);
  text-align: left;
  cursor: pointer;
}

.panel-toggle strong {
  display: block;
  margin-top: 4px;
  font-size: 15px;
}

.rotated {
  transform: rotate(180deg);
}

.form-region {
  padding: 18px;
  border-top: 1px solid var(--border);
  --form-label: #46576b;
}

:global(html.dark) .form-region {
  --form-label: #aebbd0;
}

.list-panel {
  padding: 18px;
}

.filter-box {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
}

.search-field {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 42px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--t3);
}

.search-field input,
.date-row input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--t1);
  font-size: 13px;
}

.segmented {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.segmented button,
.pick-btn {
  min-height: 34px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--t2);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.segmented button.active,
.pick-btn.active {
  border-color: var(--accent);
  background: var(--accent);
  color: #fff;
}

.date-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.date-row input {
  min-height: 38px;
  padding: 0 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
}

.map-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
}

.map-header span {
  display: block;
  margin-bottom: 3px;
  color: var(--t1);
  font-weight: 800;
}

.map-header small {
  display: block;
}

.pick-btn {
  padding: 0 12px;
  white-space: nowrap;
}

.map-body {
  height: min(66vh, 680px);
  min-height: 520px;
}

.depto-panel {
  padding: 16px;
}

.depto-row {
  grid-template-columns: 20px minmax(0, 140px) 1fr 28px;
}

.depto-row > span {
  color: var(--t3);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}

.depto-row div {
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--border);
}

.depto-row i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}

.empty-note {
  margin: 0;
  color: var(--t3);
  font-size: 13px;
}

.toast-area {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 50;
  display: grid;
  gap: 10px;
}

.toast {
  max-width: 320px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--t1);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.14);
  font-size: 13px;
}

.toast-success {
  border-color: #bbf7d0;
  color: #16a34a;
}

.toast-info {
  border-color: var(--accent);
  color: var(--accent);
}

.toast-warning {
  border-color: #fde68a;
  color: #d97706;
}

.icon {
  width: 19px;
  height: 19px;
}

.icon-sm {
  width: 16px;
  height: 16px;
}

.spinner {
  animation: spin 0.8s linear infinite;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.24s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1180px) {
  .overview-grid,
  .work-grid {
    grid-template-columns: 1fr;
  }

  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .map-panel {
    position: static;
  }
}

@media (max-width: 760px) {
  .dash-header {
    align-items: flex-start;
    flex-direction: column;
    padding: 14px 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .dashboard-shell {
    padding: 16px;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .work-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .map-body {
    min-height: 420px;
  }

  .date-row {
    grid-template-columns: 1fr;
  }
}

/* ── Pagination ───────────────────────────────── */
.pagination {
  display: flex;
  align-items: center;
  gap: 4px;
  padding-top: 12px;
  margin-top: 10px;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
}

.pg-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 6px;
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--bg);
  color: var(--t2);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}

.pg-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}

.pg-btn:disabled {
  opacity: 0.35;
  cursor: default;
}

.pg-active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff !important;
}

.pg-ellipsis {
  font-size: 12px;
  color: var(--t3);
  padding: 0 2px;
}

.pg-info {
  margin-left: auto;
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--t3);
  white-space: nowrap;
}

/* ── Credits footer ───────────────────────────── */
.credits-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 8px 28px;
  border-top: 1px solid var(--border);
  background: var(--surface);
  flex-wrap: wrap;
}

.credits-label {
  font-size: 9px;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--t3);
  white-space: nowrap;
}

.credits-orgs {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.credits-org {
  display: flex;
  align-items: center;
  gap: 6px;
}

.credits-org span {
  font-size: 10px;
  font-weight: 600;
  color: var(--t2);
  white-space: nowrap;
}

.credits-logo {
  height: 24px;
  width: auto;
  max-width: 40px;
  object-fit: contain;
  flex-shrink: 0;
  border-radius: 3px;
}

.credits-divider {
  width: 1px;
  height: 20px;
  background: var(--border);
  flex-shrink: 0;
}
</style>
