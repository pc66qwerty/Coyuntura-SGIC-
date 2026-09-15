export const tiposEvento = [
  {
    nombre: 'Emergencia',
    color: '#dc2626',
    colorLight: '#fef2f2',
    colorBorder: '#fca5a5',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>',
  },
  {
    nombre: 'Accidente vial',
    color: '#ea580c',
    colorLight: '#fff7ed',
    colorBorder: '#fdba74',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12"/>',
  },
  {
    nombre: 'Bloqueo',
    color: '#7c3aed',
    colorLight: '#f5f3ff',
    colorBorder: '#c4b5fd',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>',
  },
  {
    nombre: 'Asistencia vial',
    color: '#2563eb',
    colorLight: '#eff6ff',
    colorBorder: '#93c5fd',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z"/>',
  },
  {
    nombre: 'Trabajos',
    color: '#d97706',
    colorLight: '#fffbeb',
    colorBorder: '#fcd34d',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>',
  },
  {
    nombre: 'Libre',
    color: '#16a34a',
    colorLight: '#f0fdf4',
    colorBorder: '#86efac',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>',
  },
]

export function getTipo(nombre) {
  return tiposEvento.find((t) => t.nombre === nombre) || tiposEvento[0]
}

export function buildMarkerHtml(tipoNombre, isActivo) {
  const tipo = getTipo(tipoNombre)
  const color = isActivo ? tipo.color : '#6b7280'
  const pulse = isActivo ? 'marker-pulse' : ''
  return `
    <div style="
      position:relative;width:32px;height:32px;border-radius:50%;
      background:${color};display:flex;align-items:center;justify-content:center;
      border:2px solid rgba(255,255,255,0.3);box-shadow:0 2px 8px rgba(0,0,0,0.4);
    " class="${pulse}">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke-width="2" stroke="white" style="width:16px;height:16px;">
        ${tipo.iconPath}
      </svg>
    </div>
  `
}
