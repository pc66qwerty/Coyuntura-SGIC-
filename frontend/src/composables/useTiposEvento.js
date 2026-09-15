import { ref } from 'vue'
import api from '@/api'
import { tiposEvento as fallback } from '@/data/tiposEvento'

const tipos = ref([])
const loaded = ref(false)

export function useTiposEvento() {
  async function load(force = false) {
    if (loaded.value && !force) return
    try {
      const { data } = await api.get('/api/tipos-evento')
      tipos.value = data.map((t) => ({
        nombre: t.nombre,
        color: t.color,
        colorLight: t.color_light,
        colorBorder: t.color_border,
        iconPath: t.icon_path,
      }))
      loaded.value = true
    } catch {
      tipos.value = fallback
      loaded.value = true
    }
  }

  function getTipo(nombre) {
    return tipos.value.find((t) => t.nombre === nombre) || tipos.value[0]
  }

  function buildMarkerHtml(tipoNombre, isActivo) {
    const tipo = getTipo(tipoNombre)
    const color = isActivo ? (tipo?.color || '#6b7280') : '#6b7280'
    const pulse = isActivo ? 'marker-pulse' : ''
    const svg = tipo?.iconPath || ''
    return `
      <div style="
        position:relative;
        width:32px;
        height:32px;
        border-radius:50%;
        background:${color};
        display:flex;
        align-items:center;
        justify-content:center;
        border:2px solid rgba(255,255,255,0.3);
        box-shadow:0 2px 8px rgba(0,0,0,0.4);
      " class="${pulse}">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
          stroke-width="2" stroke="white" style="width:16px;height:16px;">
          ${svg}
        </svg>
      </div>
    `
  }

  return { tipos, loaded, load, getTipo, buildMarkerHtml }
}
