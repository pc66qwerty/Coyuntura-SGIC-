<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import html2canvas from 'html2canvas'
import ExcelJS from 'exceljs'
import { useAuthStore } from '@/stores/auth'
import AdminMap from '@/components/AdminMap.vue'
import BloqueoForm from '@/components/BloqueoForm.vue'
import BloqueoList from '@/components/BloqueoList.vue'
import BloqueoEditModal from '@/components/BloqueoEditModal.vue'
import AppFooter from '@/components/AppFooter.vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import api from '@/api'

const auth = useAuthStore()
const isEditor = computed(() => auth.isEditor)

const { tipos, load: loadTipos, getTipo } = useTiposEvento()

const bloqueos = ref([])
const showForm = ref(false)
const pickMode = ref(false)
const pickTarget = ref('form') // 'form' | 'edit'
const pendingCoords = ref(null)
const editPendingCoords = ref(null)
const editingBloqueo = ref(null)
const adminMapRef = ref(null)
const newEventsCount = ref(0)
const toasts = ref([])
const lastUpdated = ref(null)
const listSearch = ref('')
const listEstado = ref('Todos')
const dateFrom = ref('')
const dateTo = ref('')
const printLoading = ref(false)
const excelLoading = ref(false)
const currentPage = ref(1)
const PAGE_SIZE = 10

let pollInterval = null
let toastId = 0

function getTipoColor(nombre) {
  return getTipo(nombre)?.color || '#6b7280'
}

const activos = computed(() => bloqueos.value.filter((b) => b.estado === 'Activo').length)
const finalizados = computed(() => bloqueos.value.filter((b) => b.estado === 'Inactivo').length)

const tipoStats = computed(() => {
  const stats = {}
  bloqueos.value.forEach((b) => { stats[b.tipo_evento] = (stats[b.tipo_evento] || 0) + 1 })
  return stats
})

const topDeptos = computed(() => {
  const stats = {}
  bloqueos.value.filter((b) => b.estado === 'Activo').forEach((b) => { stats[b.departamento] = (stats[b.departamento] || 0) + 1 })
  return Object.entries(stats).map(([nombre, count]) => ({ nombre, count })).sort((a, b) => b.count - a.count)
})
const maxDepto = computed(() => Math.max(...topDeptos.value.map((d) => d.count), 1))

const tiempoActualizado = computed(() => {
  if (!lastUpdated.value) return null
  const s = Math.floor((Date.now() - lastUpdated.value) / 1000)
  if (s < 10) return 'justo ahora'
  if (s < 60) return `hace ${s}s`
  return `hace ${Math.floor(s / 60)}m`
})

const filteredList = computed(() => {
  let list = [...bloqueos.value]
  if (listSearch.value) {
    const q = listSearch.value.toLowerCase()
    list = list.filter((b) => [b.tipo_evento, b.municipio, b.departamento, b.direccion].some((v) => v?.toLowerCase().includes(q)))
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

function showToast(msg, type = 'success') {
  const id = ++toastId
  toasts.value.push({ id, msg, type })
  setTimeout(() => { toasts.value = toasts.value.filter((t) => t.id !== id) }, 4000)
}

async function fetchBloqueos(silent = false) {
  try {
    const prevIds = new Set(bloqueos.value.map((b) => b.id))
    const { data } = await api.get('/api/bloqueos')
    if (silent) {
      const nuevos = data.filter((b) => !prevIds.has(b.id)).length
      if (nuevos > 0) {
        newEventsCount.value += nuevos
        showToast(`${nuevos} nuevo${nuevos > 1 ? 's' : ''} evento${nuevos > 1 ? 's' : ''} registrado${nuevos > 1 ? 's' : ''} por otro editor`, 'info')
        setTimeout(() => { newEventsCount.value = 0 }, 6000)
      }
    }
    bloqueos.value = data
    lastUpdated.value = Date.now()
  } catch {
    showToast('No se pudieron cargar los eventos', 'warning')
  }
}

function onCoordsSelected(coords) {
  if (pickTarget.value === 'edit') {
    editPendingCoords.value = coords
  } else {
    pendingCoords.value = coords
  }
  pickMode.value = false
}

function togglePickMode() {
  pickTarget.value = 'form'
  pickMode.value = !pickMode.value
  if (!pickMode.value) {
    pendingCoords.value = null
    adminMapRef.value?.clearTempMarker()
  }
}

function toggleEditPickMode() {
  pickTarget.value = 'edit'
  pickMode.value = !pickMode.value
  if (!pickMode.value) {
    editPendingCoords.value = null
    adminMapRef.value?.clearTempMarker()
  } else {
    document.getElementById('admin-map-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

function onCreated(bloqueo) {
  bloqueos.value.unshift(bloqueo)
  pickMode.value = false
  pendingCoords.value = null
  adminMapRef.value?.clearTempMarker()
  adminMapRef.value?.focusOn(bloqueo.latitud, bloqueo.longitud)
  showForm.value = false
  showToast('Evento registrado correctamente', 'success')
}

function onStatusChanged(updated) {
  const idx = bloqueos.value.findIndex((b) => b.id === updated.id)
  if (idx !== -1) bloqueos.value[idx] = updated
  showToast(`Evento marcado como ${updated.estado}`, 'success')
}

function onFocusEvent(b) {
  adminMapRef.value?.focusOn(b.latitud, b.longitud)
  document.getElementById('admin-map-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function onUpdated(updated) {
  const idx = bloqueos.value.findIndex((b) => b.id === updated.id)
  if (idx !== -1) bloqueos.value[idx] = updated
  editingBloqueo.value = null
  editPendingCoords.value = null
  showToast('Evento actualizado correctamente', 'success')
}

function onDeleted(id) {
  bloqueos.value = bloqueos.value.filter((b) => b.id !== id)
  showToast('Evento eliminado', 'warning')
}

// ─── Reporte CSV ────────────────────────────────────────────────
function splitFechaHora(iso) {
  if (!iso) return { hora: '', fecha: '' }
  const d = new Date(iso)
  const hora = d.toLocaleTimeString('es-GT', { hour: '2-digit', minute: '2-digit', hour12: false })
  const fecha = d.toLocaleDateString('es-GT', { day: '2-digit', month: '2-digit', year: 'numeric' })
  return { hora, fecha }
}

// ─── Matriz completa (todas las columnas del formato institucional) ──
const showMatriz = ref(true)

const MATRIZ_COLUMNAS = [
  { key: 'no', label: 'No', align: 'right' },
  { key: 'horaInicio', label: 'Hora Inicio' },
  { key: 'fechaInicio', label: 'Fecha Inicio' },
  { key: 'tipo_evento', label: 'Tipo de Evento' },
  { key: 'estado', label: 'Estado Evento' },
  { key: 'direccion', label: 'Dirección de Inicio' },
  { key: 'x', label: 'X', align: 'right' },
  { key: 'y', label: 'Y', align: 'right' },
  { key: 'referencia_inicio', label: 'Referencia Inicio' },
  { key: 'departamento', label: 'Departamento de Inicio' },
  { key: 'municipio', label: 'Municipio de Inicio' },
  { key: 'zona_inicio', label: 'Zona Inicio' },
  { key: 'comisaria_inicio', label: 'Comisaría Inicio' },
  { key: 'manifestantes_aproximados', label: 'Personas al inicio', align: 'right' },
  { key: 'instrumentos', label: 'Instrumentos utilizados' },
  { key: 'nivel_conflicto', label: 'Nivel Conflicto' },
  { key: 'presencia_policial', label: 'Presencia Policial' },
  { key: 'cantidad_vehiculos', label: 'Cantidad Vehículos' },
  { key: 'demandas', label: 'Demandas' },
  { key: 'actores', label: 'Actores' },
  { key: 'lideres_vulnerables', label: 'Líderes / Vulnerables' },
  { key: 'horaFin', label: 'Hora Finalización' },
  { key: 'fechaFin', label: 'Fecha Finalización' },
  { key: 'direccion_fin', label: 'Dirección Finalización' },
  { key: 'coordFin', label: 'Coordenadas Finalización' },
  { key: 'referencia_fin', label: 'Referencia Finalización' },
  { key: 'duracion', label: 'Duración del Evento' },
  { key: 'departamento_fin', label: 'Departamento Finalización' },
  { key: 'municipio_fin', label: 'Municipio Finalización' },
  { key: 'zona_fin', label: 'Zona Finalización' },
  { key: 'comisaria_fin', label: 'Comisaría Finalización' },
  { key: 'personas_fin', label: 'Personas al finalizar', align: 'right' },
  { key: 'observaciones', label: 'Observaciones' },
]

const matrizRows = computed(() => filteredList.value.map((b, i) => {
  const inicio = splitFechaHora(b.fecha_hora_inicio || b.created_at)
  const fin = splitFechaHora(b.fecha_hora_fin)
  return {
    _id: b.id,
    no: i + 1,
    horaInicio: inicio.hora,
    fechaInicio: inicio.fecha,
    tipo_evento: b.tipo_evento,
    estado: b.estado,
    direccion: b.direccion,
    x: b.longitud,
    y: b.latitud,
    referencia_inicio: b.referencia_inicio || '',
    departamento: b.departamento,
    municipio: b.municipio,
    zona_inicio: b.zona_inicio || '',
    comisaria_inicio: b.comisaria_inicio || '',
    manifestantes_aproximados: b.manifestantes_aproximados || '',
    instrumentos: b.instrumentos || '',
    nivel_conflicto: b.nivel_conflicto || '',
    presencia_policial: b.presencia_policial || '',
    cantidad_vehiculos: b.cantidad_vehiculos || '',
    demandas: b.demandas || '',
    actores: b.actores || '',
    lideres_vulnerables: b.lideres_vulnerables || '',
    horaFin: fin.hora,
    fechaFin: fin.fecha,
    direccion_fin: b.direccion_fin || '',
    coordFin: (b.latitud_fin != null && b.longitud_fin != null) ? `${b.latitud_fin}, ${b.longitud_fin}` : '',
    referencia_fin: b.referencia_fin || '',
    duracion: b.duracion || '',
    departamento_fin: b.departamento_fin || '',
    municipio_fin: b.municipio_fin || '',
    zona_fin: b.zona_fin || '',
    comisaria_fin: b.comisaria_fin || '',
    personas_fin: b.personas_fin || '',
    observaciones: b.observaciones || '',
  }
}))

// ─── Paginación de la matriz ─────────────────────────────────────────────
const MATRIZ_PAGE_SIZE = 20
const matrizPage = ref(1)
const matrizTotalPages = computed(() => Math.max(1, Math.ceil(matrizRows.value.length / MATRIZ_PAGE_SIZE)))
const matrizRowsPagina = computed(() => {
  const page = Math.min(matrizPage.value, matrizTotalPages.value)
  return matrizRows.value.slice((page - 1) * MATRIZ_PAGE_SIZE, page * MATRIZ_PAGE_SIZE)
})
function goToMatrizPage(p) {
  matrizPage.value = Math.max(1, Math.min(p, matrizTotalPages.value))
}
watch(matrizRows, () => { matrizPage.value = 1 })

// Exporta la matriz institucional de eventos a un .xlsx con diseño propio
const EXCEL_COLUMNAS = [
  { key: 'no', header: 'No', width: 6, align: 'right' },
  { key: 'horaInicio', header: 'Hora Inicio', width: 11, align: 'center' },
  { key: 'fechaInicio', header: 'Fecha Inicio', width: 12, align: 'center' },
  { key: 'tipo_evento', header: 'Tipo de Evento', width: 18 },
  { key: 'estado', header: 'Estado', width: 11, align: 'center' },
  { key: 'direccion', header: 'Dirección de Inicio', width: 30 },
  { key: 'x', header: 'X', width: 12, align: 'right' },
  { key: 'y', header: 'Y', width: 12, align: 'right' },
  { key: 'referencia_inicio', header: 'Referencia Inicio', width: 24 },
  { key: 'departamento', header: 'Departamento', width: 16 },
  { key: 'municipio', header: 'Municipio', width: 16 },
  { key: 'zona_inicio', header: 'Zona', width: 8, align: 'center' },
  { key: 'comisaria_inicio', header: 'Comisaría', width: 11, align: 'center' },
  { key: 'manifestantes_aproximados', header: 'Personas al inicio', width: 14, align: 'right' },
  { key: 'instrumentos', header: 'Instrumentos utilizados', width: 28 },
  { key: 'nivel_conflicto', header: 'Nivel Conflicto', width: 13, align: 'center' },
  { key: 'presencia_policial', header: 'Presencia Policial', width: 22 },
  { key: 'cantidad_vehiculos', header: 'Cantidad Vehículos', width: 16 },
  { key: 'demandas', header: 'Demandas', width: 28 },
  { key: 'actores', header: 'Actores', width: 18 },
  { key: 'lideres_vulnerables', header: 'Líderes / Vulnerables', width: 24 },
  { key: 'horaFin', header: 'Hora Finalización', width: 13, align: 'center' },
  { key: 'fechaFin', header: 'Fecha Finalización', width: 14, align: 'center' },
  { key: 'direccion_fin', header: 'Dirección Finalización', width: 28 },
  { key: 'coordFin', header: 'Coordenadas Finalización', width: 20, align: 'center' },
  { key: 'referencia_fin', header: 'Referencia Finalización', width: 24 },
  { key: 'duracion', header: 'Duración del Evento', width: 15, align: 'center' },
  { key: 'departamento_fin', header: 'Departamento Finalización', width: 18 },
  { key: 'municipio_fin', header: 'Municipio Finalización', width: 18 },
  { key: 'zona_fin', header: 'Zona Finalización', width: 10, align: 'center' },
  { key: 'comisaria_fin', header: 'Comisaría Finalización', width: 13, align: 'center' },
  { key: 'personas_fin', header: 'Personas al finalizar', width: 15, align: 'right' },
  { key: 'observaciones', header: 'Observaciones', width: 32 },
]

const THIN_GRAY = { style: 'thin', color: { argb: 'FFE2E8F0' } }
const NIVEL_COLORES = {
  alto: { fill: 'FFFEE2E2', font: 'FFDC2626' },
  medio: { fill: 'FFFEF3C7', font: 'FFB45309' },
  bajo: { fill: 'FFDCFCE7', font: 'FF16A34A' },
}

async function exportExcel() {
  if (excelLoading.value) return
  excelLoading.value = true
  try {
    const wb = new ExcelJS.Workbook()
    wb.creator = 'Coyuntura SGIC'
    wb.created = new Date()

    const ws = wb.addWorksheet('Matriz de Eventos', {
      views: [{ state: 'frozen', ySplit: 3, showGridLines: false }],
      pageSetup: { orientation: 'landscape', fitToPage: true, fitToWidth: 1, fitToHeight: 0 },
    })
    ws.columns = EXCEL_COLUMNAS.map((c) => ({ key: c.key, width: c.width }))

    const totalCols = EXCEL_COLUMNAS.length
    const ahora = new Date()
    const fechaLarga = ahora.toLocaleDateString('es-GT', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })
    const horaStr = ahora.toLocaleTimeString('es-GT', { hour: '2-digit', minute: '2-digit' })

    // Fila 1: título institucional
    ws.mergeCells(1, 1, 1, totalCols)
    const titleCell = ws.getCell(1, 1)
    titleCell.value = 'COYUNTURA SGIC — MATRIZ DE EVENTOS VIALES'
    titleCell.font = { bold: true, size: 14, color: { argb: 'FFFFFFFF' } }
    titleCell.alignment = { vertical: 'middle', horizontal: 'left', indent: 1 }
    titleCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFDC2626' } }
    ws.getRow(1).height = 26

    // Fila 2: subtítulo con fecha de generación e instituciones
    ws.mergeCells(2, 1, 2, totalCols)
    const subtitleCell = ws.getCell(2, 1)
    subtitleCell.value = `CRADIC · SGIC · SESIC   —   Generado el ${fechaLarga.charAt(0).toUpperCase() + fechaLarga.slice(1)} a las ${horaStr} horas   —   ${bloqueos.value.length} evento${bloqueos.value.length !== 1 ? 's' : ''} registrado${bloqueos.value.length !== 1 ? 's' : ''}`
    subtitleCell.font = { italic: true, size: 9, color: { argb: 'FF6B7280' } }
    subtitleCell.alignment = { vertical: 'middle', horizontal: 'left', indent: 1 }
    subtitleCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF3F4F6' } }
    ws.getRow(2).height = 18

    // Fila 3: encabezados de columna
    const headerRow = ws.getRow(3)
    EXCEL_COLUMNAS.forEach((c, i) => {
      const cell = headerRow.getCell(i + 1)
      cell.value = c.header
      cell.font = { bold: true, size: 9, color: { argb: 'FFFFFFFF' } }
      cell.alignment = { vertical: 'middle', horizontal: c.align || 'left', wrapText: true }
      cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF111827' } }
      cell.border = { top: THIN_GRAY, bottom: THIN_GRAY, left: THIN_GRAY, right: THIN_GRAY }
    })
    headerRow.height = 32
    ws.autoFilter = { from: { row: 3, column: 1 }, to: { row: 3, column: totalCols } }

    // Filas de datos
    bloqueos.value.forEach((b, i) => {
      const inicio = splitFechaHora(b.fecha_hora_inicio || b.created_at)
      const fin = splitFechaHora(b.fecha_hora_fin)
      const row = ws.addRow({
        no: i + 1,
        horaInicio: inicio.hora,
        fechaInicio: inicio.fecha,
        tipo_evento: b.tipo_evento,
        estado: b.estado,
        direccion: b.direccion,
        x: b.longitud,
        y: b.latitud,
        referencia_inicio: b.referencia_inicio || '',
        departamento: b.departamento,
        municipio: b.municipio,
        zona_inicio: b.zona_inicio || '',
        comisaria_inicio: b.comisaria_inicio || '',
        manifestantes_aproximados: b.manifestantes_aproximados || '',
        instrumentos: b.instrumentos || '',
        nivel_conflicto: b.nivel_conflicto || '',
        presencia_policial: b.presencia_policial || '',
        cantidad_vehiculos: b.cantidad_vehiculos || '',
        demandas: b.demandas || '',
        actores: b.actores || '',
        lideres_vulnerables: b.lideres_vulnerables || '',
        horaFin: fin.hora,
        fechaFin: fin.fecha,
        direccion_fin: b.direccion_fin || '',
        coordFin: (b.latitud_fin != null && b.longitud_fin != null) ? `${b.latitud_fin}, ${b.longitud_fin}` : '',
        referencia_fin: b.referencia_fin || '',
        duracion: b.duracion || '',
        departamento_fin: b.departamento_fin || '',
        municipio_fin: b.municipio_fin || '',
        zona_fin: b.zona_fin || '',
        comisaria_fin: b.comisaria_fin || '',
        personas_fin: b.personas_fin || '',
        observaciones: b.observaciones || '',
      })

      const zebraFill = i % 2 === 1 ? { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF9FAFB' } } : null
      EXCEL_COLUMNAS.forEach((c, ci) => {
        const cell = row.getCell(ci + 1)
        cell.font = { size: 9.5, color: { argb: 'FF374151' } }
        cell.alignment = { vertical: 'middle', horizontal: c.align || 'left' }
        cell.border = { top: THIN_GRAY, bottom: THIN_GRAY, left: THIN_GRAY, right: THIN_GRAY }
        if (zebraFill) cell.fill = zebraFill
      })

      // Estado: resaltado tipo badge
      const estadoCell = row.getCell(EXCEL_COLUMNAS.findIndex((c) => c.key === 'estado') + 1)
      const activo = b.estado === 'Activo'
      estadoCell.font = { bold: true, size: 9.5, color: { argb: activo ? 'FFDC2626' : 'FF16A34A' } }
      estadoCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: activo ? 'FFFEE2E2' : 'FFDCFCE7' } }

      // Nivel de conflicto: resaltado tipo badge
      const nivel = (b.nivel_conflicto || '').toLowerCase()
      if (NIVEL_COLORES[nivel]) {
        const nivelCell = row.getCell(EXCEL_COLUMNAS.findIndex((c) => c.key === 'nivel_conflicto') + 1)
        nivelCell.font = { bold: true, size: 9.5, color: { argb: NIVEL_COLORES[nivel].font } }
        nivelCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: NIVEL_COLORES[nivel].fill } }
      }

      row.height = 18
    })

    const buffer = await wb.xlsx.writeBuffer()
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `matriz_eventos_${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    excelLoading.value = false
  }
}

// ─── Reporte de impresión con membrete institucional ────────────
async function printReport() {
  if (printLoading.value) return
  printLoading.value = true
  try {
    const list = filteredList.value
    const logoUrl = window.location.origin + '/logo-sgic.png'
    const ahora = new Date()
    const fechaLarga = ahora.toLocaleDateString('es-GT', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })
    const fechaTit = ahora.toLocaleDateString('es-GT', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '-')
    const horaStr = ahora.toLocaleTimeString('es-GT', { hour: '2-digit', minute: '2-digit' })

    const conteoTipo = {}
    list.forEach((b) => { conteoTipo[b.tipo_evento] = (conteoTipo[b.tipo_evento] || 0) + 1 })
    const tiposLista = tipos.value.map((t) => ({ nombre: t.nombre, color: t.color, n: conteoTipo[t.nombre] || 0 })).filter((t) => t.n > 0)

    const conteoDepto = {}
    list.filter((b) => b.estado === 'Activo').forEach((b) => { conteoDepto[b.departamento] = (conteoDepto[b.departamento] || 0) + 1 })
    const topDeptosList = Object.entries(conteoDepto).sort((a, b) => b[1] - a[1]).slice(0, 5)

    const totalPersonas = list.reduce((s, b) => s + (parseInt(b.manifestantes_aproximados) || 0), 0)

    let mapImgTag = ''
    try {
      const mapEl = adminMapRef.value?.mapEl?.value || adminMapRef.value?.mapEl
      if (mapEl) {
        const canvas = await html2canvas(mapEl, { useCORS: true, allowTaint: false, scale: 1.5, logging: false })
        mapImgTag = `<img src="${canvas.toDataURL('image/png')}" style="width:100%;height:220px;object-fit:cover;display:block;" alt="Mapa vial Guatemala"/>`
      }
    } catch { /* sin mapa */ }

    const colorEstado = (e) => (e === 'Activo' ? '#dc2626' : '#16a34a')
    const colorNivel = (n) => {
      const v = (n || '').toLowerCase()
      if (v === 'alto') return { bg: '#fee2e2', fg: '#dc2626' }
      if (v === 'medio') return { bg: '#fef3c7', fg: '#b45309' }
      if (v === 'bajo') return { bg: '#dcfce7', fg: '#16a34a' }
      return { bg: '#f3f4f6', fg: '#9ca3af' }
    }
    const rows = list.map((b, i) => {
      const nivel = colorNivel(b.nivel_conflicto)
      const conValor = (v) => v && v !== 'Por establecer'
      return `
      <tr>
        <td style="text-align:center;color:#6b7280;font-size:10px;">${i + 1}</td>
        <td><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${colorEstado(b.estado)};margin-right:6px;"></span>${b.direccion}</td>
        <td>${b.municipio}</td>
        <td>${b.departamento}</td>
        <td>
          <span style="display:inline-block;padding:2px 8px;border-radius:3px;font-size:10px;font-weight:700;background:${getTipoColor(b.tipo_evento)}22;color:${getTipoColor(b.tipo_evento)};border:1px solid ${getTipoColor(b.tipo_evento)}55;">
            ${b.tipo_evento}
          </span>
        </td>
        <td style="text-align:center;">
          <span style="display:inline-block;padding:2px 10px;border-radius:3px;font-size:10px;font-weight:800;letter-spacing:.04em;background:${b.estado === 'Activo' ? '#fee2e2' : '#dcfce7'};color:${colorEstado(b.estado)};">
            ${b.estado.toUpperCase()}
          </span>
        </td>
        <td style="text-align:center;">
          <span style="display:inline-block;padding:2px 8px;border-radius:3px;font-size:9px;font-weight:700;background:${nivel.bg};color:${nivel.fg};">
            ${conValor(b.nivel_conflicto) ? b.nivel_conflicto.toUpperCase() : '—'}
          </span>
        </td>
        <td style="color:#374151;">${conValor(b.actores) ? b.actores : '—'}</td>
        <td style="color:#374151;">${conValor(b.demandas) ? b.demandas : '—'}</td>
        <td style="text-align:center;color:#374151;">${b.manifestantes_aproximados ? Number(b.manifestantes_aproximados).toLocaleString('es-GT') : '—'}</td>
      </tr>`
    }).join('')

    const tiposSidebar = tiposLista.map((t) => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f3f4f6;">
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="width:10px;height:10px;border-radius:50%;background:${t.color};flex-shrink:0;display:inline-block;"></span>
          <span style="font-size:11px;color:#374151;">${t.nombre}</span>
        </div>
        <span style="font-size:13px;font-weight:900;color:#111827;">${t.n}</span>
      </div>`).join('')

    const deptosHtml = topDeptosList.map(([d, n], i) => `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
        <span style="font-size:10px;font-weight:700;color:#9ca3af;min-width:14px;">${i + 1}</span>
        <div style="flex:1;">
          <div style="display:flex;justify-content:space-between;margin-bottom:2px;">
            <span style="font-size:11px;color:#374151;font-weight:600;">${d}</span>
            <span style="font-size:11px;font-weight:800;color:#dc2626;">${n}</span>
          </div>
          <div style="height:4px;background:#f3f4f6;border-radius:2px;">
            <div style="height:4px;background:#dc2626;border-radius:2px;width:${Math.round((n / topDeptosList[0][1]) * 100)}%;"></div>
          </div>
        </div>
      </div>`).join('')

    const win = window.open('', '_blank')
    if (!win) return
    win.document.write(`<!DOCTYPE html><html lang="es"><head>
      <meta charset="UTF-8">
      <title>Reporte Vial — ${fechaTit}</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @page { size: A4 landscape; margin: 12mm 14mm; }
        body { font-family: Arial, Helvetica, sans-serif; background: #fff; color: #111827; font-size: 12px; }
        .header { display: flex; align-items: stretch; border-bottom: 3px solid #dc2626; padding-bottom: 10px; margin-bottom: 14px; gap: 16px; }
        .header-logo-box { width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .header-logo-box img { width: 100%; height: 100%; object-fit: contain; }
        .header-inst { flex: 1; display: flex; flex-direction: column; justify-content: center; }
        .header-inst .line1 { font-size: 15px; font-weight: 900; color: #111827; letter-spacing: -.01em; line-height: 1.1; }
        .header-inst .line2 { font-size: 9px; color: #6b7280; text-transform: uppercase; letter-spacing: .1em; margin-top: 3px; }
        .header-inst .line3 { font-size: 9px; color: #9ca3af; margin-top: 1px; }
        .header-right { text-align: right; display: flex; flex-direction: column; justify-content: center; gap: 3px; }
        .header-right .rep-title { font-size: 11px; font-weight: 900; color: #dc2626; text-transform: uppercase; letter-spacing: .08em; }
        .header-right .rep-date  { font-size: 10px; color: #374151; font-weight: 600; }
        .header-right .rep-hora  { font-size: 9px; color: #9ca3af; }
        .header-right .rep-code  { font-size: 8px; color: #d1d5db; font-family: monospace; margin-top: 2px; }
        .statsbar { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; margin-bottom: 14px; }
        .stat { padding: 10px 14px; border-radius: 6px; border: 1px solid; }
        .stat.total      { background: #f8fafc; border-color: #e2e8f0; }
        .stat.activos    { background: #fff1f2; border-color: #fecdd3; }
        .stat.finalizados{ background: #f0fdf4; border-color: #bbf7d0; }
        .stat.personas   { background: #fefce8; border-color: #fef08a; }
        .stat-n   { font-size: 26px; font-weight: 900; line-height: 1; margin-bottom: 2px; }
        .stat-lbl { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #6b7280; }
        .stat.total       .stat-n { color: #111827; }
        .stat.activos     .stat-n { color: #dc2626; }
        .stat.finalizados .stat-n { color: #16a34a; }
        .stat.personas    .stat-n { color: #92400e; }
        .layout { display: flex; gap: 14px; }
        .sidebar { width: 190px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px; }
        .main { flex: 1; min-width: 0; }
        .panel { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; }
        .panel-title { font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: .1em; color: #6b7280; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #e5e7eb; }
        .map-box { border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden; margin-bottom: 10px; }
        .map-label { font-size: 8px; text-align:center; color:#9ca3af; padding:3px; background:#f9fafb; border-top:1px solid #e5e7eb; }
        table { width: 100%; border-collapse: collapse; font-size: 10.5px; }
        thead tr { background: #111827; }
        th { padding: 7px 8px; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: #fff; text-align: left; white-space: nowrap; }
        td { padding: 6px 8px; border-bottom: 1px solid #f3f4f6; color: #374151; vertical-align: middle; }
        tr:last-child td { border-bottom: none; }
        tr:nth-child(even) td { background: #f9fafb; }
        .footer { display: flex; align-items: center; justify-content: space-between; margin-top: 12px; padding-top: 8px; border-top: 1px solid #e5e7eb; }
        .footer-cradic { display: flex; align-items: center; gap: 6px; }
        .footer-cradic .dot { width: 6px; height: 6px; background: #dc2626; border-radius: 50%; }
        .footer-cradic span { font-size: 8px; color: #9ca3af; }
        .footer-cradic strong { color: #6b7280; }
        .footer-total { background: #dc2626; color: white; font-size: 10px; font-weight: 800; padding: 5px 14px; border-radius: 3px; text-transform: uppercase; letter-spacing: .06em; }
        .footer-page { font-size: 8px; color: #d1d5db; font-family: monospace; }
        @media print { body, .stat, thead tr, td { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
      </style>
    </head><body>
      <div class="header">
        <div class="header-logo-box">
          <img src="${logoUrl}" alt="Coyuntura SGIC" />
        </div>
        <div class="header-inst">
          <div class="line1">Coyuntura SGIC</div>
          <div class="line2">Seccion de Sistemas de Informacion Criminal &nbsp;·&nbsp; CRADIC</div>
          <div class="line3">Sistema de Monitoreo de Eventos Viales — Guatemala</div>
        </div>
        <div class="header-right">
          <div class="rep-title">Reporte de Eventos Viales</div>
          <div class="rep-date">${fechaLarga.charAt(0).toUpperCase() + fechaLarga.slice(1)}</div>
          <div class="rep-hora">Generado a las ${horaStr} horas</div>
          <div class="rep-code">REP-${fechaTit.replace(/-/g, '')}-${Math.random().toString(36).slice(2, 6).toUpperCase()}</div>
        </div>
      </div>
      <div class="statsbar">
        <div class="stat total"><div class="stat-n">${list.length}</div><div class="stat-lbl">Total de eventos</div></div>
        <div class="stat activos"><div class="stat-n">${list.filter((b) => b.estado === 'Activo').length}</div><div class="stat-lbl">En curso</div></div>
        <div class="stat finalizados"><div class="stat-n">${list.filter((b) => b.estado === 'Inactivo').length}</div><div class="stat-lbl">Inactivos</div></div>
        <div class="stat personas"><div class="stat-n">${totalPersonas > 0 ? totalPersonas.toLocaleString('es-GT') : '—'}</div><div class="stat-lbl">Personas aprox.</div></div>
      </div>
      <div class="layout">
        <div class="sidebar">
          ${mapImgTag ? `<div class="map-box">${mapImgTag}<div class="map-label">Vista actual del mapa</div></div>` : ''}
          <div class="panel">
            <div class="panel-title">Por tipo de evento</div>
            ${tiposSidebar || '<span style="font-size:11px;color:#9ca3af;">Sin datos</span>'}
          </div>
          ${topDeptosList.length ? `<div class="panel"><div class="panel-title">Departamentos activos</div>${deptosHtml}</div>` : ''}
        </div>
        <div class="main">
          <table>
            <thead><tr>
              <th style="width:30px;">#</th><th>Direccion / Referencia</th><th>Municipio</th><th>Departamento</th>
              <th>Tipo</th><th style="text-align:center;">Estado</th><th style="text-align:center;">Nivel</th>
              <th>Actores</th><th>Demandas / Motivo</th><th style="text-align:center;">Personas</th>
            </tr></thead>
            <tbody>${rows || '<tr><td colspan="10" style="text-align:center;color:#9ca3af;padding:20px;">Sin eventos registrados</td></tr>'}</tbody>
          </table>
        </div>
      </div>
      <div class="footer">
        <div class="footer-cradic">
          <div class="dot"></div>
          <span><strong>Seccion de Sistemas de Informacion Criminal</strong> &nbsp;|&nbsp; CRADIC &nbsp;|&nbsp; Coyuntura SGIC</span>
        </div>
        ${totalPersonas > 0 ? `<div class="footer-total">${totalPersonas.toLocaleString('es-GT')} personas aproximadas</div>` : ''}
        <div class="footer-page">Documento generado el ${fechaTit} a las ${horaStr}</div>
      </div>
      <script>window.onload = () => setTimeout(() => window.print(), 300)<\/script>
    </body></html>`)
    win.document.close()
  } finally {
    printLoading.value = false
  }
}

onMounted(async () => {
  await loadTipos()
  await fetchBloqueos()
  pollInterval = setInterval(() => fetchBloqueos(true), 30000)
})

onUnmounted(() => { if (pollInterval) clearInterval(pollInterval) })
</script>

<template>
  <div class="min-h-screen bg-[#EEF2FA] dark:bg-[#131314] px-4 sm:px-6 lg:px-8 py-6">
    <div class="max-w-[1600px] mx-auto space-y-6">

      <!-- Page header -->
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <router-link to="/" class="text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition" aria-label="Volver al mapa principal">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
            </svg>
          </router-link>
          <div>
            <h1 class="text-xl font-black text-gray-900 dark:text-white">Panel de Control</h1>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Gestión de eventos viales en tiempo real</p>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <!-- Última actualización -->
          <div v-if="tiempoActualizado" class="hidden sm:flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-full px-3 py-1.5 border border-gray-200 dark:border-gray-700">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span class="text-xs text-gray-500 dark:text-gray-400">{{ tiempoActualizado }}</span>
          </div>
          <span class="px-2.5 py-1 rounded-full text-xs font-bold border"
            :class="isEditor
              ? 'bg-indigo-50 text-indigo-600 border-indigo-200 dark:bg-indigo-900/40 dark:text-indigo-300 dark:border-indigo-700'
              : 'bg-gray-100 text-gray-500 border-gray-200 dark:bg-gray-700 dark:text-gray-400 dark:border-gray-600'">
            {{ isEditor ? 'Editor' : 'Lector' }}
          </span>
          <router-link to="/usuarios"
            class="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 rounded-lg hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 shadow-sm transition">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            Usuarios
          </router-link>
          <router-link to="/tipos-evento"
            class="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 rounded-lg hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 shadow-sm transition">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Tipos
          </router-link>
          <button @click="exportExcel" :disabled="excelLoading"
            class="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 rounded-lg hover:border-green-500 hover:text-green-600 dark:hover:text-green-400 shadow-sm transition disabled:opacity-50">
            <svg v-if="!excelLoading" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            <svg v-else class="animate-spin h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            <span class="hidden sm:inline">Exportar</span> Excel
          </button>
          <button @click="printReport" :disabled="printLoading"
            class="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 rounded-lg hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 shadow-sm transition disabled:opacity-50">
            <svg v-if="!printLoading" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
            </svg>
            <svg v-else class="animate-spin h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            <span class="hidden sm:inline">Imprimir /</span> PDF
          </button>
        </div>
      </div>

      <!-- Alerta nuevos eventos -->
      <transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition duration-200" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="newEventsCount > 0" class="flex items-center gap-3 bg-indigo-600 text-white text-sm font-semibold px-4 py-3 rounded-2xl shadow-lg">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
          </svg>
          {{ newEventsCount }} nuevo{{ newEventsCount > 1 ? 's' : '' }} evento{{ newEventsCount > 1 ? 's' : '' }} registrado{{ newEventsCount > 1 ? 's' : '' }} por otro editor
          <button @click="newEventsCount = 0" class="ml-auto opacity-70 hover:opacity-100">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </transition>

      <!-- Stats cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-4 flex items-center gap-3 shadow-sm">
          <div class="w-10 h-10 bg-[#EEF2FA] dark:bg-[#252525] rounded-xl flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
          </div>
          <div>
            <p class="text-2xl font-black text-gray-900 dark:text-white leading-none">{{ bloqueos.length }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Total eventos</p>
          </div>
        </div>
        <div class="bg-red-50 dark:bg-gray-800 border border-red-200 dark:border-red-900/40 rounded-2xl p-4 flex items-center gap-3 shadow-sm">
          <div class="w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
            <span class="w-4 h-4 rounded-full bg-red-500 shadow shadow-red-500/50"></span>
          </div>
          <div>
            <p class="text-2xl font-black text-red-500 dark:text-red-400 leading-none">{{ activos }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-0.5">Activos</p>
          </div>
        </div>
        <div class="bg-green-50 dark:bg-gray-800 border border-green-200 dark:border-green-900/40 rounded-2xl p-4 flex items-center gap-3 shadow-sm">
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
            <span class="w-4 h-4 rounded-full bg-green-500 shadow shadow-green-500/50"></span>
          </div>
          <div>
            <p class="text-2xl font-black text-green-600 dark:text-green-400 leading-none">{{ finalizados }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-0.5">Inactivos</p>
          </div>
        </div>
        <div class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-4 shadow-sm">
          <p class="text-xs text-gray-500 dark:text-gray-500 mb-3 font-semibold uppercase tracking-wider">Por tipo</p>
          <div class="space-y-2">
            <div v-for="tipo in tipos.filter(t => tipoStats[t.nombre])" :key="tipo.nombre">
              <div class="flex items-center justify-between mb-0.5">
                <span class="text-xs text-gray-600 dark:text-gray-400 truncate">{{ tipo.nombre }}</span>
                <span class="text-xs font-black ml-2 flex-shrink-0" :style="`color:${tipo.color}`">{{ tipoStats[tipo.nombre] }}</span>
              </div>
              <div class="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-500"
                  :style="`width:${Math.round(tipoStats[tipo.nombre] / bloqueos.length * 100)}%;background:${tipo.color}`">
                </div>
              </div>
            </div>
            <p v-if="!bloqueos.length" class="text-xs text-gray-400 dark:text-gray-600 italic">Sin datos</p>
          </div>
        </div>
      </div>

      <!-- Top departamentos activos -->
      <div v-if="topDeptos.length > 0" class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-4 shadow-sm">
        <div class="flex items-center gap-2 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.243-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <p class="text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Focos activos por departamento</p>
          <span class="ml-auto text-xs text-gray-400 dark:text-gray-500">{{ activos }} activo{{ activos !== 1 ? 's' : '' }} en total</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div v-for="(d, i) in topDeptos" :key="d.nombre"
            class="flex items-center gap-3 bg-[#EEF2FA] dark:bg-[#1A1A1A] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-xl p-3">
            <div class="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-black text-white flex-shrink-0"
              :class="i === 0 ? 'bg-red-500' : i === 1 ? 'bg-orange-500' : 'bg-gray-500'">
              {{ i + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-gray-800 dark:text-gray-200 truncate">{{ d.nombre }}</p>
              <div class="mt-1 h-1 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                <div class="h-full bg-red-500 rounded-full transition-all duration-500" :style="`width:${Math.round(d.count / maxDepto * 100)}%`"></div>
              </div>
            </div>
            <span class="text-lg font-black text-red-500 flex-shrink-0">{{ d.count }}</span>
          </div>
        </div>
      </div>

      <!-- Main layout: left (form + list) | right (map) -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">

        <!-- Left column -->
        <div class="space-y-5">
          <!-- Formulario colapsable -->
          <div>
            <button @click="showForm = !showForm"
              class="w-full flex items-center justify-between px-4 py-3 bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl hover:border-red-400 transition group shadow-sm"
              :class="showForm ? 'rounded-b-none border-b-0' : ''">
              <span class="flex items-center gap-2 text-sm font-bold text-gray-800 dark:text-gray-200 group-hover:text-red-500 transition">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Registrar Nuevo Evento
              </span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 transition-transform duration-200" :class="showForm ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <transition
              enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 -translate-y-1" enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition duration-150 ease-in" leave-from-class="opacity-100" leave-to-class="opacity-0 -translate-y-1">
              <div v-if="showForm" class="border border-t-0 border-[#E2E8F0] dark:border-[#2A2A2A] rounded-b-2xl overflow-hidden">
                <BloqueoForm
                  :pending-coords="pendingCoords"
                  :pick-mode="pickMode && pickTarget === 'form'"
                  @created="onCreated"
                  @toggle-pick-mode="togglePickMode"
                  @focus-location="adminMapRef?.focusOn($event.lat, $event.lng, $event.zoom)"
                />
              </div>
            </transition>
          </div>

          <!-- List header + filtros -->
          <div class="space-y-2">
            <h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2 px-1">
              <span class="w-1 h-4 bg-indigo-500 rounded-full"></span>
              Eventos Registrados
              <span class="text-gray-400 dark:text-gray-500 font-normal">
                ({{ filteredList.length }}{{ filteredList.length !== bloqueos.length ? ` de ${bloqueos.length}` : '' }})
              </span>
            </h3>
            <div class="flex gap-2">
              <div class="relative flex-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
                <input v-model="listSearch" type="text" placeholder="Buscar evento, lugar..."
                  class="w-full bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-xl pl-8 pr-3 py-1.5 text-xs text-gray-700 dark:text-gray-300 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-400 transition shadow-sm"/>
              </div>
              <div class="flex rounded-xl border border-[#E2E8F0] dark:border-[#2A2A2A] overflow-hidden text-xs font-semibold shadow-sm">
                <button v-for="opt in ['Todos', 'Activo', 'Inactivo']" :key="opt"
                  @click="listEstado = opt"
                  class="px-2.5 py-1.5 transition"
                  :class="listEstado === opt
                    ? 'bg-[#E8EDF5] dark:bg-[#2A2A2A] text-gray-800 dark:text-white'
                    : 'bg-white dark:bg-[#1C1C1E] text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'">
                  {{ opt }}
                </button>
              </div>
            </div>
            <!-- Filtro de fechas -->
            <div class="flex items-center gap-2 flex-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-gray-400 dark:text-gray-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <input v-model="dateFrom" type="date"
                class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-lg px-2 py-1 text-xs text-gray-700 dark:text-gray-300 focus:outline-none focus:border-indigo-400 transition shadow-sm cursor-pointer"/>
              <span class="text-xs text-gray-400 dark:text-gray-500">—</span>
              <input v-model="dateTo" type="date"
                class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-lg px-2 py-1 text-xs text-gray-700 dark:text-gray-300 focus:outline-none focus:border-indigo-400 transition shadow-sm cursor-pointer"/>
              <button v-if="dateFrom || dateTo" @click="dateFrom = ''; dateTo = ''" class="text-xs text-gray-400 hover:text-red-500 transition px-1">✕ Limpiar</button>
            </div>
          </div>

          <div class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-3 shadow-sm">
            <BloqueoList
              :bloqueos="pagedList"
              :can-edit="true"
              @status-changed="onStatusChanged"
              @focus-event="onFocusEvent"
              @edit-event="editingBloqueo = $event"
              @deleted="onDeleted"
            />

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="flex items-center gap-1 pt-3 mt-2 border-t border-[#E2E8F0] dark:border-[#2A2A2A] flex-wrap">
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
                {{ (currentPage - 1) * PAGE_SIZE + 1 }}–{{ Math.min(currentPage * PAGE_SIZE, filteredList.length) }} de {{ filteredList.length }}
              </span>
            </div>
          </div>
        </div>

        <!-- Right column: Map -->
        <div id="admin-map-section">
          <div class="sticky top-6">
            <div class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl p-4 shadow-sm">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                  </svg>
                  Mapa en Tiempo Real
                </h3>
                <span v-if="pickMode"
                  class="text-xs font-bold px-2.5 py-1 rounded-full border animate-pulse text-blue-600 bg-blue-50 border-blue-300 dark:text-blue-400 dark:bg-blue-900/40 dark:border-blue-700">
                  Modo selección activo
                </span>
              </div>
              <p class="text-xs text-gray-400 dark:text-gray-500 mb-3">
                Usa <strong class="text-gray-500 dark:text-gray-400">"Elegir punto"</strong> en el formulario para fijar coordenadas. El ícono
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 inline text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.243-4.243a8 8 0 1111.314 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                en la lista centra el mapa.
              </p>
              <div class="h-[min(66vh,680px)] min-h-[520px] rounded-xl overflow-hidden">
                <AdminMap
                  ref="adminMapRef"
                  :bloqueos="filteredList"
                  :pick-mode="pickMode"
                  @coords-selected="onCoordsSelected"
                />
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Matriz completa de eventos -->
      <div class="bg-white dark:bg-[#1C1C1E] border border-[#E2E8F0] dark:border-[#2A2A2A] rounded-2xl overflow-hidden">
        <button @click="showMatriz = !showMatriz"
          class="w-full flex items-center justify-between px-4 py-3.5 text-left hover:bg-gray-50 dark:hover:bg-[#242424] transition">
          <span class="flex items-center gap-2">
            <span class="w-1 h-4 bg-red-500 rounded-full"></span>
            <span class="text-sm font-bold text-gray-900 dark:text-white">Matriz completa de eventos</span>
            <span class="text-xs text-gray-400 dark:text-gray-500 font-normal">({{ matrizRows.length }} · formato institucional)</span>
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 transition-transform duration-200" :class="showMatriz ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>
        <div v-if="showMatriz" class="border-t border-[#E2E8F0] dark:border-[#2A2A2A] overflow-x-auto">
          <table class="text-xs border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-[#161616] sticky top-0">
                <th v-for="col in MATRIZ_COLUMNAS" :key="col.key"
                  class="px-3 py-2 font-mono text-[10px] uppercase tracking-wide text-gray-400 dark:text-gray-500 border-b border-[#E2E8F0] dark:border-[#2A2A2A] whitespace-nowrap"
                  :class="col.align === 'right' ? 'text-right' : 'text-left'">
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in matrizRowsPagina" :key="row._id" class="border-b border-[#F0F0F0] dark:border-[#252525] last:border-b-0 hover:bg-gray-50 dark:hover:bg-[#242424] transition-colors">
                <td v-for="col in MATRIZ_COLUMNAS" :key="col.key"
                  class="px-3 py-2 whitespace-nowrap max-w-[220px] truncate text-gray-600 dark:text-gray-300"
                  :class="[
                    col.align === 'right' ? 'text-right' : 'text-left',
                    col.key === 'estado' ? (row.estado === 'Activo' ? 'font-bold text-red-600 dark:text-red-400' : 'font-bold text-gray-400 dark:text-gray-500') : '',
                  ]"
                  :title="row[col.key]">
                  {{ row[col.key] || '—' }}
                </td>
              </tr>
              <tr v-if="matrizRows.length === 0">
                <td :colspan="MATRIZ_COLUMNAS.length" class="px-3 py-8 text-center text-gray-400 dark:text-gray-500">Sin eventos que coincidan con los filtros</td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination -->
          <div v-if="matrizTotalPages > 1" class="flex items-center gap-1 px-3 py-3 border-t border-[#E2E8F0] dark:border-[#2A2A2A] flex-wrap">
            <button class="w-8 h-8 flex items-center justify-center rounded-lg border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 text-xs font-bold disabled:opacity-35 hover:border-indigo-400 hover:text-indigo-500 transition"
              :disabled="matrizPage <= 1" @click="goToMatrizPage(matrizPage - 1)" type="button">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5"/></svg>
            </button>
            <template v-for="p in matrizTotalPages" :key="p">
              <button v-if="p === 1 || p === matrizTotalPages || Math.abs(p - matrizPage) <= 1"
                class="min-w-8 h-8 px-1 flex items-center justify-center rounded-lg border text-xs font-bold transition"
                :class="p === matrizPage
                  ? 'bg-indigo-600 border-indigo-600 text-white'
                  : 'border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 hover:border-indigo-400 hover:text-indigo-500'"
                @click="goToMatrizPage(p)" type="button">{{ p }}</button>
              <span v-else-if="p === matrizPage - 2 || p === matrizPage + 2" class="text-xs text-gray-400 px-0.5">…</span>
            </template>
            <button class="w-8 h-8 flex items-center justify-center rounded-lg border border-[#E2E8F0] dark:border-[#2A2A2A] text-gray-500 dark:text-gray-400 text-xs font-bold disabled:opacity-35 hover:border-indigo-400 hover:text-indigo-500 transition"
              :disabled="matrizPage >= matrizTotalPages" @click="goToMatrizPage(matrizPage + 1)" type="button">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/></svg>
            </button>
            <span class="ml-auto text-xs font-mono text-gray-400 dark:text-gray-500 whitespace-nowrap">
              {{ (matrizPage - 1) * MATRIZ_PAGE_SIZE + 1 }}–{{ Math.min(matrizPage * MATRIZ_PAGE_SIZE, matrizRows.length) }} de {{ matrizRows.length }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <AppFooter :status="tiempoActualizado ? `Actualización automática · ${tiempoActualizado}` : ''" />

    <!-- Edit modal (oculto mientras se selecciona ubicación en el mapa) -->
    <BloqueoEditModal
      v-if="editingBloqueo && !(pickMode && pickTarget === 'edit')"
      :bloqueo="editingBloqueo"
      :pending-coords="editPendingCoords"
      :pick-mode="pickMode && pickTarget === 'edit'"
      @updated="onUpdated"
      @close="editingBloqueo = null"
      @toggle-pick-mode="toggleEditPickMode"
    />

    <!-- Toasts -->
    <teleport to="body">
      <div class="fixed bottom-5 right-5 z-[9999] space-y-2 pointer-events-none">
        <transition-group
          enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 translate-x-4" enter-to-class="opacity-100 translate-x-0"
          leave-active-class="transition duration-200 ease-in" leave-from-class="opacity-100" leave-to-class="opacity-0 translate-x-4">
          <div v-for="t in toasts" :key="t.id"
            class="flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl text-sm font-semibold pointer-events-auto min-w-[220px]"
            :class="{
              'bg-green-600 text-white': t.type === 'success',
              'bg-indigo-600 text-white': t.type === 'info',
              'bg-orange-500 text-white': t.type === 'warning',
              'bg-red-600 text-white': t.type === 'error',
            }">
            <svg v-if="t.type === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
            <svg v-else-if="t.type === 'info'" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            </svg>
            {{ t.msg }}
          </div>
        </transition-group>
      </div>
    </teleport>
  </div>
</template>
