<script setup>
import { ref, onMounted } from 'vue'
import { useTiposEvento } from '@/composables/useTiposEvento'
import AppFooter from '@/components/AppFooter.vue'

const { tipos, load: loadTipos } = useTiposEvento()
onMounted(loadTipos)

const seccionAbierta = ref('mapa')

const secciones = [
  { id: 'mapa', label: 'El mapa principal', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
  { id: 'eventos', label: 'Tipos de evento', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  { id: 'filtros', label: 'Buscar y filtrar', icon: 'M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z' },
  { id: 'panel', label: 'Panel de control', icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z' },
  { id: 'registro', label: 'Registrar un evento', icon: 'M12 4v16m8-8H4' },
  { id: 'roles', label: 'Roles de usuario', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z' },
]
</script>

<template>
  <div class="min-h-screen bg-slate-100 dark:bg-gray-950">

    <div class="max-w-4xl mx-auto px-4 py-8">

      <!-- Encabezado -->
      <div class="mb-8">
        <div class="flex items-center gap-3 mb-2">
          <router-link to="/" class="text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition" title="Volver al mapa">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
            </svg>
          </router-link>
          <div class="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center shadow">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-black text-gray-900 dark:text-white">Centro de Ayuda</h1>
            <p class="text-sm text-gray-500 dark:text-gray-400">Guía de uso del sistema Coyuntura SGIC</p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">

        <!-- Navegacion lateral -->
        <nav class="lg:col-span-1">
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-3 sticky top-4">
            <p class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-3 mb-2">Secciones</p>
            <button v-for="s in secciones" :key="s.id"
              @click="seccionAbierta = s.id"
              class="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium transition-all mb-0.5"
              :class="seccionAbierta === s.id
                ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="s.icon"/>
              </svg>
              {{ s.label }}
            </button>
          </div>
        </nav>

        <!-- Contenido -->
        <div class="lg:col-span-3 space-y-4">

          <!-- EL MAPA PRINCIPAL -->
          <div v-if="seccionAbierta === 'mapa'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
            <h2 class="text-lg font-black text-gray-900 dark:text-white mb-4">El mapa principal</h2>
            <div class="space-y-4 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              <p>Al ingresar al sistema verá un mapa interactivo con todos los eventos viales registrados en Guatemala. Cada evento se representa con un marcador de color según su tipo.</p>
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                <p class="font-bold text-gray-700 dark:text-gray-200 mb-2">Cómo navegar el mapa</p>
                <ul class="space-y-1.5">
                  <li class="flex items-start gap-2"><span class="text-indigo-500 font-bold mt-0.5">+/-</span> Botones de zoom en la esquina inferior izquierda para acercar o alejar.</li>
                  <li class="flex items-start gap-2"><span class="text-indigo-500 font-bold mt-0.5">Arrastrar</span> Mantén presionado y mueve para desplazarte por el mapa.</li>
                  <li class="flex items-start gap-2"><span class="text-indigo-500 font-bold mt-0.5">Clic en marcador</span> Hace zoom automático al evento y muestra su información detallada.</li>
                </ul>
              </div>
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                <p class="font-bold text-gray-700 dark:text-gray-200 mb-2">Botones del mapa</p>
                <ul class="space-y-1.5">
                  <li><span class="font-semibold text-gray-700 dark:text-gray-300">Mapa Claro / Oscuro:</span> Cambia el estilo del mapa entre modo oscuro y modo estándar (OpenStreetMap).</li>
                  <li><span class="font-semibold text-gray-700 dark:text-gray-300">Sol / Luna (esquina superior):</span> Cambia el tema visual de toda la interfaz entre claro y oscuro.</li>
                </ul>
              </div>
              <p class="text-xs text-gray-400 dark:text-gray-500">Los marcadores con animación de pulso son eventos activos en curso. Los marcadores opacos son eventos finalizados.</p>
            </div>
          </div>

          <!-- TIPOS DE EVENTO -->
          <div v-if="seccionAbierta === 'eventos'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
            <h2 class="text-lg font-black text-gray-900 dark:text-white mb-4">Tipos de evento</h2>
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">El sistema maneja los siguientes tipos de evento vial. Cada uno tiene un color e ícono distinto en el mapa para identificarse rápidamente.</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div v-for="tipo in tipos" :key="tipo.nombre"
                class="flex items-center gap-3 p-3 rounded-xl border border-gray-100 dark:border-gray-700">
                <span class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                  :style="`background:${tipo.color}`">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" v-html="tipo.iconPath"/>
                </span>
                <div>
                  <p class="font-bold text-sm text-gray-800 dark:text-gray-200">{{ tipo.nombre }}</p>
                </div>
              </div>
            </div>
            <div class="mt-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4 text-sm text-amber-700 dark:text-amber-400">
              Al registrar un evento, debe seleccionar el tipo que mejor describe la situación vial reportada. Un Editor puede crear tipos adicionales desde la sección "Tipos de evento" del panel.
            </div>
          </div>

          <!-- BUSCAR Y FILTRAR -->
          <div v-if="seccionAbierta === 'filtros'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
            <h2 class="text-lg font-black text-gray-900 dark:text-white mb-4">Buscar y filtrar eventos</h2>
            <div class="space-y-4 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              <p>En la página principal puedes filtrar los eventos usando el panel de filtros sobre la lista de eventos.</p>
              <div class="space-y-3">
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <p class="font-bold text-gray-700 dark:text-gray-200 mb-2">Búsqueda por texto</p>
                  <p>Escribe cualquier término en el campo de búsqueda: tipo de evento, dirección, municipio o departamento. La lista y el mapa se actualizan en tiempo real.</p>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <p class="font-bold text-gray-700 dark:text-gray-200 mb-2">Filtro por período</p>
                  <p>Filtra eventos por cuándo fueron registrados: Hoy, Ayer, Últimos 7 días, Últimos 30 días, Todo, o un rango de fechas personalizado.</p>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <p class="font-bold text-gray-700 dark:text-gray-200 mb-2">Filtro por estado, tipo y departamento</p>
                  <p>Selecciona Activo/Inactivo, un tipo de evento específico o un departamento para ver solo esos marcadores en el mapa y esas tarjetas en la lista.</p>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <p class="font-bold text-gray-700 dark:text-gray-200 mb-2">Ordenar resultados</p>
                  <p>Puedes ordenar la lista por más reciente, más antiguo o mostrando los eventos activos primero.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- PANEL DE CONTROL -->
          <div v-if="seccionAbierta === 'panel'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
            <h2 class="text-lg font-black text-gray-900 dark:text-white mb-4">Panel de control</h2>
            <div class="space-y-4 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              <p>El panel de control es accesible solo para usuarios con rol de <strong class="text-gray-800 dark:text-gray-200">Editor</strong>. Desde aquí puedes gestionar todos los eventos del sistema.</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <p class="font-bold text-gray-700 dark:text-gray-200 mb-1">Estadísticas</p>
                  <p>Resumen de eventos totales, activos, finalizados y un desglose por tipo de evento.</p>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <p class="font-bold text-gray-700 dark:text-gray-200 mb-1">Focos por departamento</p>
                  <p>Ranking de los departamentos con más eventos activos en el momento.</p>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <p class="font-bold text-gray-700 dark:text-gray-200 mb-1">Lista de eventos</p>
                  <p>Puedes buscar, filtrar por estado y fechas, y realizar acciones sobre cada evento registrado.</p>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <p class="font-bold text-gray-700 dark:text-gray-200 mb-1">Actualización automática</p>
                  <p>El panel se actualiza cada 30 segundos y notifica cuando otro editor registra un nuevo evento.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- REGISTRAR UN EVENTO -->
          <div v-if="seccionAbierta === 'registro'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
            <h2 class="text-lg font-black text-gray-900 dark:text-white mb-4">Registrar un evento</h2>
            <div class="space-y-3 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              <p>Solo los usuarios con rol <strong class="text-gray-800 dark:text-gray-200">Editor</strong> pueden registrar, editar y eliminar eventos.</p>
              <ol class="space-y-3">
                <li class="flex gap-3">
                  <span class="w-6 h-6 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center font-black text-xs flex-shrink-0 mt-0.5">1</span>
                  <div><strong class="text-gray-700 dark:text-gray-300">Abra el panel de control</strong> — desde el botón "Panel" en el mapa principal, y despliegue "Registrar Nuevo Evento".</div>
                </li>
                <li class="flex gap-3">
                  <span class="w-6 h-6 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center font-black text-xs flex-shrink-0 mt-0.5">2</span>
                  <div><strong class="text-gray-700 dark:text-gray-300">Seleccione el tipo de evento</strong> — elija el tipo que mejor describe la situación (Bloqueo, Accidente, Emergencia, etc.).</div>
                </li>
                <li class="flex gap-3">
                  <span class="w-6 h-6 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center font-black text-xs flex-shrink-0 mt-0.5">3</span>
                  <div><strong class="text-gray-700 dark:text-gray-300">Complete departamento, municipio y dirección</strong> — describa la ubicación exacta o referencia del evento.</div>
                </li>
                <li class="flex gap-3">
                  <span class="w-6 h-6 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center font-black text-xs flex-shrink-0 mt-0.5">4</span>
                  <div><strong class="text-gray-700 dark:text-gray-300">Marque las coordenadas GPS</strong> — use "Elegir punto" y luego haga clic en el punto exacto del mapa donde ocurre el evento. Las coordenadas se llenan automáticamente.</div>
                </li>
                <li class="flex gap-3">
                  <span class="w-6 h-6 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center font-black text-xs flex-shrink-0 mt-0.5">5</span>
                  <div><strong class="text-gray-700 dark:text-gray-300">Guarde el evento</strong> — el marcador aparecerá de inmediato en el mapa y en la lista.</div>
                </li>
              </ol>
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 mt-2">
                <p class="font-bold text-blue-700 dark:text-blue-400 mb-1">Actualizar estado</p>
                <p class="text-blue-600 dark:text-blue-300">Cuando un evento se resuelve, cambie su estado a <strong>Inactivo</strong> desde la lista del panel. Esto mantiene el historial y retira la animación del marcador.</p>
              </div>
            </div>
          </div>

          <!-- ROLES DE USUARIO -->
          <div v-if="seccionAbierta === 'roles'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
            <h2 class="text-lg font-black text-gray-900 dark:text-white mb-4">Roles de usuario</h2>
            <div class="space-y-4 text-sm text-gray-600 dark:text-gray-300">
              <div class="border border-indigo-200 dark:border-indigo-800 rounded-xl overflow-hidden">
                <div class="bg-indigo-50 dark:bg-indigo-900/30 px-4 py-3 flex items-center gap-2">
                  <span class="w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center text-white font-black text-xs">E</span>
                  <p class="font-bold text-indigo-700 dark:text-indigo-400">Editor</p>
                </div>
                <div class="p-4 space-y-1">
                  <p>— Acceso completo al mapa y al panel de control.</p>
                  <p>— Puede registrar, editar y eliminar eventos.</p>
                  <p>— Puede gestionar usuarios (crear, cambiar roles, restablecer contraseñas, eliminar).</p>
                  <p>— Puede exportar reportes en CSV y PDF.</p>
                </div>
              </div>
              <div class="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
                <div class="bg-gray-50 dark:bg-gray-700/50 px-4 py-3 flex items-center gap-2">
                  <span class="w-6 h-6 bg-gray-500 rounded-full flex items-center justify-center text-white font-black text-xs">L</span>
                  <p class="font-bold text-gray-700 dark:text-gray-300">Lector</p>
                </div>
                <div class="p-4 space-y-1">
                  <p>— Acceso al mapa principal para consulta.</p>
                  <p>— Puede visualizar todos los eventos activos y finalizados.</p>
                  <p>— Puede usar los filtros de búsqueda.</p>
                  <p>— No puede registrar ni modificar eventos.</p>
                  <p>— No tiene acceso al panel de control.</p>
                </div>
              </div>
              <p class="text-xs text-gray-400 dark:text-gray-500">Los usuarios son creados por un Editor desde la sección Usuarios del panel.</p>
            </div>
          </div>

        </div>
      </div>

    </div>

    <AppFooter />
  </div>
</template>
