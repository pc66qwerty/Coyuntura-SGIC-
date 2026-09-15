<template>
  <div class="min-h-screen flex flex-col" style="background:var(--bg)">
    <!-- Nav -->
    <nav class="border-b" style="background:var(--surface);border-color:var(--border)">
      <div class="max-w-5xl mx-auto px-6 py-4 flex items-center gap-4">
        <router-link to="/" class="transition-colors" style="color:var(--t2)">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
          </svg>
        </router-link>
        <span class="font-display font-semibold" style="color:var(--t1)">Centro de Ayuda</span>
      </div>
    </nav>

    <div class="flex flex-1 max-w-5xl mx-auto w-full">
      <!-- Sidebar -->
      <aside class="w-56 shrink-0 p-5 border-r hidden md:block" style="background:var(--surface);border-color:var(--border)">
        <p class="font-mono text-xs uppercase tracking-wide mb-3" style="color:var(--t3)">Secciones</p>
        <ul class="space-y-1">
          <li v-for="s in sections" :key="s.id">
            <button @click="active = s.id"
              class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors font-medium"
              :style="active === s.id
                ? 'background:var(--accent);color:#fff'
                : 'color:var(--t2)'">
              {{ s.title }}
            </button>
          </li>
        </ul>
      </aside>

      <!-- Content -->
      <main class="flex-1 p-8 overflow-y-auto">
        <!-- Mobile nav -->
        <div class="md:hidden mb-6 flex gap-2 overflow-x-auto pb-2">
          <button v-for="s in sections" :key="s.id" @click="active = s.id"
            class="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors border"
            :style="active === s.id
              ? 'background:var(--accent);color:#fff;border-color:var(--accent)'
              : 'color:var(--t2);background:var(--surface);border-color:var(--border)'">
            {{ s.title }}
          </button>
        </div>

        <!-- El mapa -->
        <div v-if="active === 'mapa'">
          <h1 class="font-display font-bold text-xl mb-4" style="color:var(--t1)">El mapa principal</h1>
          <div class="space-y-4 text-sm leading-relaxed" style="color:var(--t2)">
            <p>El mapa principal muestra todos los eventos viales registrados en tiempo real sobre un mapa interactivo de Guatemala.</p>
            <div v-for="card in mapaCards" :key="card.title" class="rounded-xl p-4 border" style="background:var(--surface);border-color:var(--border)">
              <p class="font-medium mb-2" style="color:var(--t1)">{{ card.title }}</p>
              <ul class="space-y-1" style="color:var(--t2)">
                <li v-for="item in card.items" :key="item">• {{ item }}</li>
              </ul>
            </div>
            <p>El mapa se actualiza automáticamente cada 20 segundos. Recibirás una notificación cuando otro editor registre un nuevo evento.</p>
          </div>
        </div>

        <!-- Tipos de evento -->
        <div v-if="active === 'tipos'">
          <h1 class="font-display font-bold text-xl mb-2" style="color:var(--t1)">Tipos de evento</h1>
          <p class="text-sm mb-6" style="color:var(--t2)">Cada tipo tiene un color e icono distintivo para identificarlo rápidamente en el mapa.</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="tipo in tiposEvento" :key="tipo.nombre"
              class="flex items-center gap-3 rounded-xl p-3 border"
              style="background:var(--surface);border-color:var(--border)">
              <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0" :style="{ background: tipo.color }">
                <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
                  <path stroke-linecap="round" stroke-linejoin="round" :d="tipo.iconD" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-sm" style="color:var(--t1)">{{ tipo.nombre }}</p>
                <p class="text-xs" style="color:var(--t2)">{{ tipo.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Filtros -->
        <div v-if="active === 'filtros'">
          <h1 class="font-display font-bold text-xl mb-4" style="color:var(--t1)">Buscar y filtrar eventos</h1>
          <div class="space-y-4 text-sm leading-relaxed" style="color:var(--t2)">
            <div v-for="card in filtroCards" :key="card.title" class="rounded-xl p-4 border" style="background:var(--surface);border-color:var(--border)">
              <p class="font-medium mb-2" style="color:var(--t1)">{{ card.title }}</p>
              <ul class="space-y-1">
                <li v-for="item in card.items" :key="item">• {{ item }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Dashboard -->
        <div v-if="active === 'dashboard'">
          <h1 class="font-display font-bold text-xl mb-4" style="color:var(--t1)">Panel de control</h1>
          <p class="text-sm mb-4" style="color:var(--t2)">El panel de control está disponible solo para usuarios con rol Editor.</p>
          <div class="space-y-3">
            <div v-for="card in dashboardCards" :key="card.title" class="rounded-xl p-4 border" style="background:var(--surface);border-color:var(--border)">
              <p class="font-medium text-sm mb-1" style="color:var(--t1)">{{ card.title }}</p>
              <p class="text-sm" style="color:var(--t2)">{{ card.body }}</p>
            </div>
          </div>
        </div>

        <!-- Registrar -->
        <div v-if="active === 'registrar'">
          <h1 class="font-display font-bold text-xl mb-4" style="color:var(--t1)">Registrar un evento</h1>
          <p class="text-sm mb-5" style="color:var(--t2)">Solo los usuarios Editor pueden registrar eventos. Sigue estos pasos:</p>
          <ol class="space-y-4">
            <li v-for="(step, i) in steps" :key="i" class="flex gap-4">
              <span class="w-7 h-7 rounded-full text-white text-sm font-semibold flex items-center justify-center shrink-0" style="background:var(--accent)">{{ i + 1 }}</span>
              <div>
                <p class="font-medium text-sm" style="color:var(--t1)">{{ step.title }}</p>
                <p class="text-xs mt-1" style="color:var(--t2)">{{ step.desc }}</p>
              </div>
            </li>
          </ol>
        </div>

        <!-- Roles -->
        <div v-if="active === 'roles'">
          <h1 class="font-display font-bold text-xl mb-4" style="color:var(--t1)">Roles de usuario</h1>
          <div class="space-y-4">
            <div class="rounded-xl p-5 border" style="background:var(--accent-dim);border-color:var(--accent)">
              <div class="flex items-center gap-3 mb-3">
                <span class="px-2.5 py-0.5 text-white text-xs font-semibold rounded-full" style="background:var(--accent)">Editor</span>
                <span class="font-medium text-sm" style="color:var(--t1)">Acceso completo</span>
              </div>
              <ul class="text-sm space-y-1.5" style="color:var(--t2)">
                <li v-for="item in editorPerms" :key="item">✓ {{ item }}</li>
              </ul>
            </div>
            <div class="rounded-xl p-5 border" style="background:var(--surface);border-color:var(--border)">
              <div class="flex items-center gap-3 mb-3">
                <span class="px-2.5 py-0.5 text-white text-xs font-semibold rounded-full" style="background:var(--t2)">Lector</span>
                <span class="font-medium text-sm" style="color:var(--t1)">Solo lectura</span>
              </div>
              <ul class="text-sm space-y-1.5" style="color:var(--t2)">
                <li v-for="item in lectorPerms" :key="item.text" :style="item.denied ? 'color:var(--t3)' : ''">
                  {{ item.denied ? '✗' : '✓' }} {{ item.text }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const active = ref('mapa')

const sections = [
  { id: 'mapa',      title: 'El mapa principal' },
  { id: 'tipos',     title: 'Tipos de evento' },
  { id: 'filtros',   title: 'Buscar y filtrar' },
  { id: 'dashboard', title: 'Panel de control' },
  { id: 'registrar', title: 'Registrar evento' },
  { id: 'roles',     title: 'Roles de usuario' },
]

const mapaCards = [
  { title: 'Navegación:', items: ['Zoom: Rueda del ratón o botones +/-', 'Mover: Clic y arrastrar', 'Ver evento: Clic en cualquier marcador'] },
  { title: 'Marcadores:', items: ['Los marcadores con animación pulsante son eventos activos', 'Los marcadores grises son eventos finalizados', 'El color de cada marcador corresponde al tipo de evento'] },
  { title: 'Controles del mapa:', items: ['Tema mapa: Alterna entre mapa oscuro y claro', 'Tema UI: Alterna entre interfaz oscura y clara', 'Botón Panel: Acceso al dashboard (solo editores)'] },
]

const filtroCards = [
  { title: 'Búsqueda por texto', items: ['Busca en tipo de evento, municipio, departamento o dirección'] },
  { title: 'Filtro por período', items: ['Hoy / Ayer: Solo eventos del día seleccionado', 'Últimos 7/30 días: Ventana móvil de tiempo', 'Todos: Sin límite de tiempo', 'Rango personalizado: Selecciona fecha inicio y fin'] },
  { title: 'Otros filtros', items: ['Estado: Activo, Finalizado o Todos', 'Tipo de evento: Filtra por categoría', 'Departamento: Solo eventos de ese departamento', 'Ordenar: Más reciente, Más antiguo, Activos primero'] },
]

const dashboardCards = [
  { title: 'Estadísticas en tiempo real', body: 'Total, activos y finalizados con porcentajes. Desglose por tipo de evento y top departamentos con más actividad.' },
  { title: 'Lista de eventos', body: 'Busca, filtra y gestiona todos los eventos. Enfoca el mapa, edita, cambia estado o elimina eventos directamente desde la lista.' },
  { title: 'Reportes', body: 'Exporta en CSV para hojas de cálculo, o genera un reporte PDF con estadísticas y tabla completa de eventos.' },
  { title: 'Auto-actualización', body: 'Los datos se actualizan automáticamente cada 30 segundos. Recibirás una notificación cuando otro editor registre eventos.' },
]

const steps = [
  { title: 'Seleccionar tipo de evento', desc: 'Elige el tipo que mejor describe la situación.' },
  { title: 'Seleccionar ubicación', desc: 'Escoge el departamento y municipio. El mapa se centrará automáticamente en esa área.' },
  { title: 'Ingresar dirección', desc: 'Usa los prefijos rápidos para agilizar el ingreso.' },
  { title: 'Seleccionar coordenadas', desc: 'Haz clic en "Seleccionar en mapa" y luego en el punto exacto para obtener las coordenadas GPS.' },
  { title: 'Datos adicionales y envío', desc: 'Agrega cantidad de personas, observaciones y foto opcional. Haz clic en "Registrar evento".' },
]

const editorPerms = ['Ver mapa y eventos', 'Registrar nuevos eventos', 'Editar y eliminar eventos', 'Cambiar estado (Activo/Finalizado)', 'Gestionar usuarios', 'Exportar reportes CSV y PDF', 'Acceder al panel de control']
const lectorPerms = [
  { text: 'Ver mapa en tiempo real', denied: false },
  { text: 'Ver detalles de eventos', denied: false },
  { text: 'Filtrar y buscar eventos', denied: false },
  { text: 'Consultar el centro de ayuda', denied: false },
  { text: 'Registrar o editar eventos', denied: true },
  { text: 'Gestionar usuarios', denied: true },
  { text: 'Exportar reportes', denied: true },
]

const tiposEvento = [
  { nombre: 'Emergencia',    color: '#dc2626', desc: 'Situaciones de emergencia inmediata', iconD: 'M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z' },
  { nombre: 'Accidente vial',color: '#ea580c', desc: 'Colisiones y accidentes de tránsito',  iconD: 'M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25' },
  { nombre: 'Bloqueo',       color: '#7c3aed', desc: 'Cierre o bloqueo de vía',              iconD: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' },
  { nombre: 'Asistencia vial',color:'#2563eb', desc: 'Asistencia mecánica o remolque',       iconD: 'M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877' },
  { nombre: 'Trabajos',      color: '#d97706', desc: 'Obras viales o mantenimiento',          iconD: 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z' },
  { nombre: 'Libre',         color: '#16a34a', desc: 'Vía despejada o resuelta',              iconD: 'M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
]
</script>
