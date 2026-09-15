<template>
  <div class="h-screen flex flex-col overflow-hidden" style="background:var(--bg)">
    <!-- Header -->
    <header class="shrink-0 border-b relative z-[1000]" style="background:var(--surface);border-color:var(--border)">
      <div class="px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background:var(--accent)">
            <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c-.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"/>
            </svg>
          </div>
          <span class="font-display font-semibold text-sm hidden sm:block" style="color:var(--t1)">Monitor Vial</span>
          <span class="font-mono text-xs hidden lg:block" style="color:var(--t3)">Monitoreo en tiempo real</span>
        </div>

        <div class="flex items-center gap-1">
          <!-- Map theme toggle -->
          <button @click="toggleMapTheme"
            class="px-2.5 py-1.5 rounded-lg text-xs flex items-center gap-1.5 transition-colors"
            style="color:var(--t2)"
            @mouseover="$event.currentTarget.style.background='var(--bg)'"
            @mouseleave="$event.currentTarget.style.background='transparent'">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c-.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"/>
            </svg>
            <span class="hidden sm:block font-mono text-xs">{{ mapDark ? 'Mapa oscuro' : 'Mapa claro' }}</span>
          </button>

          <div class="theme-switch" aria-label="Tema visual">
            <button type="button" :class="{ active: theme === 'light' }" @click="applyTheme('light')">Claro</button>
            <button type="button" :class="{ active: theme === 'dark' }" @click="applyTheme('dark')">Oscuro</button>
          </div>

          <router-link v-if="auth.isEditor" to="/dashboard"
            class="flex items-center gap-1.5 px-3 py-1.5 text-white text-xs font-medium rounded-lg transition-colors"
            style="background:var(--accent)"
            @mouseover="$event.currentTarget.style.background='var(--accent-hi)'"
            @mouseleave="$event.currentTarget.style.background='var(--accent)'">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/>
            </svg>
            <span class="hidden sm:block">Panel</span>
          </router-link>

          <!-- User menu -->
          <div class="relative" ref="menuRef">
            <button @click="showMenu = !showMenu"
              class="flex items-center gap-2 px-2 py-1.5 rounded-lg transition-colors"
              @mouseover="$event.currentTarget.style.background='var(--bg)'"
              @mouseleave="$event.currentTarget.style.background='transparent'">
              <div class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-semibold" style="background:var(--accent)">
                {{ auth.user?.name?.[0]?.toUpperCase() }}
              </div>
              <span class="text-sm hidden sm:block" style="color:var(--t1)">{{ auth.user?.name }}</span>
            </button>
            <div v-if="showMenu" class="absolute right-0 top-full mt-1 w-48 rounded-xl shadow-lg overflow-hidden z-[2000] border" style="background:var(--surface);border-color:var(--border)">
              <router-link v-if="auth.isEditor" to="/dashboard" @click="showMenu = false"
                class="flex items-center gap-2 px-4 py-2.5 text-sm transition-colors font-medium"
                style="color:var(--accent)"
                @mouseover="$event.currentTarget.style.background='var(--bg)'"
                @mouseleave="$event.currentTarget.style.background='transparent'">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/></svg>
                Panel de control
              </router-link>
              <div v-if="auth.isEditor" class="border-t my-1" style="border-color:var(--border)"></div>
              <router-link to="/perfil" @click="showMenu = false"
                class="flex items-center gap-2 px-4 py-2.5 text-sm transition-colors"
                style="color:var(--t2)"
                @mouseover="$event.currentTarget.style.background='var(--bg)'"
                @mouseleave="$event.currentTarget.style.background='transparent'">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/></svg>
                Mi perfil
              </router-link>
              <router-link to="/ayuda" @click="showMenu = false"
                class="flex items-center gap-2 px-4 py-2.5 text-sm transition-colors"
                style="color:var(--t2)"
                @mouseover="$event.currentTarget.style.background='var(--bg)'"
                @mouseleave="$event.currentTarget.style.background='transparent'">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"/></svg>
                Ayuda
              </router-link>
              <div class="border-t my-1" style="border-color:var(--border)"></div>
              <button @click="logout"
                class="w-full flex items-center gap-2 px-4 py-2.5 text-sm transition-colors"
                style="color:#DC2626"
                @mouseover="$event.currentTarget.style.background='var(--bg)'"
                @mouseleave="$event.currentTarget.style.background='transparent'">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"/></svg>
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- New event toast -->
    <Transition name="event-toast">
      <div v-if="showNewEventToast"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-[2000] flex items-center gap-3 pl-4 pr-3 py-3 rounded-2xl shadow-2xl overflow-hidden"
        style="background:#1E3A5F;min-width:260px;max-width:380px">
        <!-- Pulse ring -->
        <div class="relative shrink-0">
          <span class="absolute inset-0 rounded-full animate-ping opacity-40" style="background:#7DD3FC"></span>
          <div class="relative w-8 h-8 rounded-full flex items-center justify-center" style="background:rgba(125,211,252,0.18)">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="#7DD3FC">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"/>
            </svg>
          </div>
        </div>
        <!-- Text -->
        <div class="flex-1 min-w-0">
          <p class="text-xs font-semibold uppercase tracking-widest" style="color:#7DD3FC">Nuevo evento</p>
          <p class="text-sm font-semibold text-white leading-tight mt-0.5">
            {{ newEventsCount }} evento{{ newEventsCount > 1 ? 's' : '' }} registrado{{ newEventsCount > 1 ? 's' : '' }}
          </p>
        </div>
        <!-- Close -->
        <button @click="dismissNewEventToast" class="shrink-0 w-6 h-6 rounded-full flex items-center justify-center transition-colors" style="color:#93c5fd" @mouseover="$event.currentTarget.style.background='rgba(255,255,255,0.1)'" @mouseleave="$event.currentTarget.style.background='transparent'">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
        <!-- Progress bar -->
        <div class="absolute bottom-0 left-0 h-0.5 w-full" style="background:rgba(255,255,255,0.12)">
          <div class="h-full event-toast-progress" style="background:#7DD3FC"></div>
        </div>
      </div>
    </Transition>

    <!-- Main content -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Map -->
      <div class="flex-1 relative">
        <div id="welcome-map" class="w-full h-full"></div>

        <!-- Stats panel (desktop) -->
        <div class="absolute bottom-4 left-4 z-[500] hidden lg:block">
          <div class="rounded-xl p-4 min-w-[200px] shadow-sm border backdrop-blur-sm" style="background:var(--surface);border-color:var(--border);opacity:.97">
            <p class="font-mono text-xs uppercase tracking-widest font-semibold mb-3" style="color:var(--t2)">Estadísticas</p>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm" style="color:var(--t2)">Total</span>
                <span class="font-semibold" style="color:var(--t1)">{{ bloqueos.length }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm" style="color:var(--t2)">Activos</span>
                <span class="font-semibold" style="color:#DC2626">{{ activos }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm" style="color:var(--t2)">Finalizados</span>
                <span class="font-semibold" style="color:#16A34A">{{ finalizados }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Selected event card -->
        <div v-if="selectedBloqueo" class="absolute top-4 left-4 right-4 sm:right-auto sm:w-80 z-[1000]">
          <div class="rounded-xl shadow-lg overflow-hidden border backdrop-blur-sm" style="background:var(--surface);border-color:var(--border)">
            <div class="flex items-center justify-between p-4 border-b" style="border-color:var(--border)">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0" :style="{ background: getTipoColor(selectedBloqueo.tipo_evento) }">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="white">
                    <path stroke-linecap="round" stroke-linejoin="round" :d="getTipoIcon(selectedBloqueo.tipo_evento)" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium" style="color:var(--t1)">{{ selectedBloqueo.tipo_evento }}</p>
                  <span class="text-xs px-1.5 py-0.5 rounded-full font-medium border"
                    :style="selectedBloqueo.estado === 'Activo'
                      ? 'background:#FEF2F2;color:#DC2626;border-color:#FECACA'
                      : 'background:#F0FDF4;color:#16A34A;border-color:#BBF7D0'">
                    {{ selectedBloqueo.estado }}
                  </span>
                </div>
              </div>
              <button @click="selectedBloqueo = null" style="color:var(--t3)" @mouseover="$event.currentTarget.style.color='var(--t1)'" @mouseleave="$event.currentTarget.style.color='var(--t3)'">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
            <div class="p-4 space-y-2 text-sm">
              <p style="color:var(--t2)"><span style="color:var(--t3)">Dirección:</span> {{ selectedBloqueo.direccion }}</p>
              <p style="color:var(--t2)"><span style="color:var(--t3)">Municipio:</span> {{ selectedBloqueo.municipio }}, {{ selectedBloqueo.departamento }}</p>
              <p v-if="selectedBloqueo.manifestantes_aproximados" style="color:var(--t2)">
                <span style="color:var(--t3)">Personas aprox.:</span> {{ selectedBloqueo.manifestantes_aproximados }}
              </p>
              <p v-if="selectedBloqueo.observaciones" style="color:var(--t2)">
                <span style="color:var(--t3)">Observaciones:</span> {{ selectedBloqueo.observaciones }}
              </p>
              <p class="font-mono text-xs" style="color:var(--t3)">{{ selectedBloqueo.latitud.toFixed(6) }}, {{ selectedBloqueo.longitud.toFixed(6) }}</p>
              <p v-if="selectedBloqueo.estado === 'Finalizado' && selectedBloqueo.updated_at" class="text-xs" style="color:var(--t3)">
                <span>Finalizado:</span> {{ fmtDate(selectedBloqueo.updated_at) }}
              </p>
              <img v-if="selectedBloqueo.foto_path" :src="selectedBloqueo.foto_path" class="w-full rounded-lg mt-2 max-h-40 object-cover border" style="border-color:var(--border)" />
            </div>
          </div>
        </div>
      </div>

      <!-- Filters panel -->
      <aside class="w-96 shrink-0 flex flex-col overflow-hidden border-l max-lg:hidden" style="background:var(--surface);border-color:var(--border)">
        <!-- Search -->
        <div class="p-4 border-b shrink-0" style="border-color:var(--border)">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--t3)" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>
            </svg>
            <input v-model="searchText" type="text" placeholder="Buscar eventos..."
              class="w-full pl-9 pr-4 py-2 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'" />
          </div>
        </div>

        <!-- Filters -->
        <div class="p-4 space-y-4 shrink-0 border-b" style="border-color:var(--border)">
          <!-- Period -->
          <div>
            <label class="font-mono text-xs uppercase tracking-widest font-semibold mb-2 block" style="color:var(--t2)">Período</label>
            <div class="grid grid-cols-3 gap-1">
              <button v-for="p in periods" :key="p.value" @click="period = p.value"
                class="py-1 text-xs rounded-lg transition-colors font-medium"
                :style="period === p.value
                  ? 'background:var(--accent);color:#fff'
                  : 'background:var(--bg);color:var(--t2)'">
                {{ p.label }}
              </button>
            </div>
          </div>

          <!-- Estado -->
          <div>
            <label class="font-mono text-xs uppercase tracking-widest font-semibold mb-2 block" style="color:var(--t2)">Estado</label>
            <div class="flex gap-1">
              <button v-for="e in ['Todos', 'Activo', 'Finalizado']" :key="e" @click="estadoFilter = e"
                class="flex-1 py-1 text-xs rounded-lg transition-colors font-medium"
                :style="estadoFilter === e
                  ? 'background:var(--accent);color:#fff'
                  : 'background:var(--bg);color:var(--t2)'">
                {{ e }}
              </button>
            </div>
          </div>

          <!-- Tipo -->
          <div>
            <label class="font-mono text-xs uppercase tracking-widest font-semibold mb-2 block" style="color:var(--t2)">Tipo de evento</label>
            <select v-model="tipoFilter"
              class="w-full px-3 py-1.5 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'">
              <option value="">Todos los tipos</option>
              <option v-for="t in tiposUnicos" :key="t">{{ t }}</option>
            </select>
          </div>

          <!-- Depto -->
          <div>
            <label class="font-mono text-xs uppercase tracking-widest font-semibold mb-2 block" style="color:var(--t2)">Departamento</label>
            <select v-model="deptoFilter"
              class="w-full px-3 py-1.5 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'">
              <option value="">Todos</option>
              <option v-for="d in deptosUnicos" :key="d">{{ d }}</option>
            </select>
          </div>

          <!-- Sort -->
          <div>
            <label class="font-mono text-xs uppercase tracking-widest font-semibold mb-2 block" style="color:var(--t2)">Ordenar</label>
            <select v-model="sortBy"
              class="w-full px-3 py-1.5 rounded-lg text-sm outline-none transition-colors border"
              style="background:var(--bg);border-color:var(--border);color:var(--t1)"
              @focus="$event.target.style.borderColor='var(--accent)'"
              @blur="$event.target.style.borderColor='var(--border)'">
              <option value="newest">Más reciente</option>
              <option value="oldest">Más antiguo</option>
              <option value="active">Activos primero</option>
            </select>
          </div>

          <button @click="clearFilters"
            class="w-full py-1.5 text-xs rounded-lg transition-colors font-medium"
            style="background:var(--bg);color:var(--t2)"
            @mouseover="$event.currentTarget.style.background='var(--border)'"
            @mouseleave="$event.currentTarget.style.background='var(--bg)'">
            Limpiar filtros
          </button>
        </div>

        <!-- Event list -->
        <div class="flex-1 overflow-y-auto p-3 space-y-2">
          <p class="font-mono text-xs px-1" style="color:var(--t3)">{{ filtered.length }} resultado{{ filtered.length !== 1 ? 's' : '' }}</p>
          <div v-for="b in filtered" :key="b.id"
            @click="focusEvent(b)"
            class="rounded-lg p-3 cursor-pointer transition-all border"
            style="background:var(--surface);border-color:var(--border)"
            @mouseover="$event.currentTarget.style.background='var(--bg)'"
            @mouseleave="$event.currentTarget.style.background='var(--surface)'">
            <div class="flex items-center justify-between mb-1">
              <div class="flex items-center gap-2">
                <div class="w-5 h-5 rounded-full shrink-0" :style="{ background: getTipoColor(b.tipo_evento) }"></div>
                <span class="text-xs font-medium" style="color:var(--t1)">{{ b.tipo_evento }}</span>
              </div>
              <span class="text-xs px-1.5 py-0.5 rounded-full font-medium"
                :style="b.estado === 'Activo'
                  ? 'background:#FEF2F2;color:#DC2626'
                  : 'background:#F0FDF4;color:#16A34A'">
                {{ b.estado }}
              </span>
            </div>
            <p class="text-xs truncate" style="color:var(--t2)">{{ b.municipio }}, {{ b.departamento }}</p>
            <p class="text-xs truncate" style="color:var(--t3)">{{ b.direccion }}</p>
            <p class="font-mono text-xs mt-1" style="color:var(--t3)">{{ timeAgo(b.created_at) }}</p>
          </div>
          <div v-if="filtered.length === 0" class="text-center py-8 text-sm" style="color:var(--t3)">
            No hay eventos con esos filtros
          </div>

          <!-- Stats section -->
          <div class="mt-4 pt-4 border-t space-y-3" style="border-color:var(--border)">
            <p class="font-mono text-xs uppercase tracking-widest font-semibold px-1" style="color:var(--t2)">Estadísticas</p>

            <!-- Totals -->
            <div class="grid grid-cols-3 gap-2">
              <div class="rounded-lg p-2.5 text-center border" style="background:var(--bg);border-color:var(--border)">
                <p class="text-lg font-semibold" style="color:var(--t1)">{{ bloqueos.length }}</p>
                <p class="font-mono text-xs" style="color:var(--t3)">Total</p>
              </div>
              <div class="rounded-lg p-2.5 text-center border" style="background:#FEF2F2;border-color:#FECACA">
                <p class="text-lg font-semibold" style="color:#DC2626">{{ activos }}</p>
                <p class="font-mono text-xs" style="color:#DC2626;opacity:.7">Activos</p>
              </div>
              <div class="rounded-lg p-2.5 text-center border" style="background:#F0FDF4;border-color:#BBF7D0">
                <p class="text-lg font-semibold" style="color:#16A34A">{{ finalizados }}</p>
                <p class="font-mono text-xs" style="color:#16A34A;opacity:.7">Fin.</p>
              </div>
            </div>

            <!-- Por tipo -->
            <div v-if="tipoStats.length > 0" class="rounded-lg border p-3 space-y-2" style="background:var(--bg);border-color:var(--border)">
              <p class="font-mono text-xs uppercase tracking-widest font-semibold" style="color:var(--t2)">Por tipo</p>
              <div v-for="item in tipoStats" :key="item.tipo" class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: getTipoColor(item.tipo) }"></div>
                <span class="text-xs flex-1 truncate" style="color:var(--t2)">{{ item.tipo }}</span>
                <div class="w-16 rounded-full h-1" style="background:var(--border)">
                  <div class="h-1 rounded-full" :style="{ background: getTipoColor(item.tipo), width: (item.count / bloqueos.length * 100) + '%' }"></div>
                </div>
                <span class="font-mono text-xs w-4 text-right" style="color:var(--t1)">{{ item.count }}</span>
              </div>
            </div>

            <!-- Top departamentos -->
            <div v-if="topDeptos.length > 0" class="rounded-lg border p-3 space-y-2" style="background:var(--bg);border-color:var(--border)">
              <p class="font-mono text-xs uppercase tracking-widest font-semibold" style="color:var(--t2)">Top departamentos</p>
              <div v-for="(item, i) in topDeptos" :key="item.nombre" class="flex items-center gap-2">
                <span class="font-mono text-xs w-3 shrink-0" style="color:var(--t3)">{{ i + 1 }}</span>
                <span class="text-xs flex-1 truncate" style="color:var(--t2)">{{ item.nombre }}</span>
                <span class="font-mono text-xs font-medium" style="color:var(--t1)">{{ item.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Mobile filter button -->
    <button @click="showMobileFilters = true"
      class="lg:hidden fixed bottom-5 right-5 z-[800] flex items-center gap-2 px-4 py-2.5 text-white text-sm font-medium rounded-full shadow-lg transition-colors"
      style="background:var(--accent)">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12"/>
      </svg>
      Filtros y lista
    </button>

    <!-- Mobile filter drawer -->
    <div v-if="showMobileFilters" class="lg:hidden fixed inset-0 z-[900] flex flex-col justify-end">
      <div class="absolute inset-0 bg-black/50" @click="showMobileFilters = false"></div>
      <div class="relative flex flex-col rounded-t-2xl max-h-[88vh] overflow-hidden border-t" style="background:var(--surface);border-color:var(--border)">
        <!-- Handle -->
        <div class="flex items-center justify-between px-5 py-3 border-b shrink-0" style="border-color:var(--border)">
          <span class="font-display font-semibold" style="color:var(--t1)">Eventos y filtros</span>
          <button @click="showMobileFilters = false" style="color:var(--t2)">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div class="overflow-y-auto flex-1">
          <!-- Search -->
          <div class="p-4 border-b" style="border-color:var(--border)">
            <div class="relative">
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--t3)" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>
              </svg>
              <input v-model="searchText" type="text" placeholder="Buscar eventos..."
                class="w-full pl-9 pr-4 py-2 rounded-lg text-sm outline-none transition-colors border"
                style="background:var(--bg);border-color:var(--border);color:var(--t1)" />
            </div>
          </div>

          <!-- Filters -->
          <div class="p-4 space-y-3 border-b" style="border-color:var(--border)">
            <div>
              <label class="font-mono text-xs uppercase tracking-widest font-semibold mb-2 block" style="color:var(--t2)">Período</label>
              <div class="grid grid-cols-5 gap-1">
                <button v-for="p in periods" :key="p.value" @click="period = p.value"
                  class="py-1.5 text-xs rounded-lg transition-colors font-medium"
                  :style="period === p.value ? 'background:var(--accent);color:#fff' : 'background:var(--bg);color:var(--t2)'">
                  {{ p.label }}
                </button>
              </div>
            </div>
            <div>
              <label class="font-mono text-xs uppercase tracking-widest font-semibold mb-2 block" style="color:var(--t2)">Estado</label>
              <div class="flex gap-1">
                <button v-for="e in ['Todos', 'Activo', 'Finalizado']" :key="e" @click="estadoFilter = e"
                  class="flex-1 py-1.5 text-xs rounded-lg transition-colors font-medium"
                  :style="estadoFilter === e ? 'background:var(--accent);color:#fff' : 'background:var(--bg);color:var(--t2)'">
                  {{ e }}
                </button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <select v-model="tipoFilter" class="px-2 py-1.5 rounded-lg text-sm outline-none border" style="background:var(--bg);border-color:var(--border);color:var(--t1)">
                <option value="">Todos los tipos</option>
                <option v-for="t in tiposUnicos" :key="t">{{ t }}</option>
              </select>
              <select v-model="deptoFilter" class="px-2 py-1.5 rounded-lg text-sm outline-none border" style="background:var(--bg);border-color:var(--border);color:var(--t1)">
                <option value="">Todos los deptos.</option>
                <option v-for="d in deptosUnicos" :key="d">{{ d }}</option>
              </select>
            </div>
            <button @click="clearFilters"
              class="w-full py-1.5 text-xs rounded-lg font-medium border transition-colors"
              style="background:var(--bg);color:var(--t2);border-color:var(--border)">
              Limpiar filtros
            </button>
          </div>

          <!-- Event list -->
          <div class="p-3 space-y-2">
            <p class="font-mono text-xs px-1" style="color:var(--t3)">{{ filtered.length }} resultado{{ filtered.length !== 1 ? 's' : '' }}</p>
            <div v-for="b in filtered" :key="b.id"
              @click="focusEvent(b); showMobileFilters = false"
              class="rounded-lg p-3 cursor-pointer transition-all border"
              style="background:var(--surface);border-color:var(--border)">
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2">
                  <div class="w-4 h-4 rounded-full shrink-0" :style="{ background: getTipoColor(b.tipo_evento) }"></div>
                  <span class="text-xs font-medium" style="color:var(--t1)">{{ b.tipo_evento }}</span>
                </div>
                <span class="text-xs px-1.5 py-0.5 rounded-full font-medium"
                  :style="b.estado === 'Activo' ? 'background:#FEF2F2;color:#DC2626' : 'background:#F0FDF4;color:#16A34A'">
                  {{ b.estado }}
                </span>
              </div>
              <p class="text-xs truncate" style="color:var(--t2)">{{ b.municipio }}, {{ b.departamento }}</p>
              <p class="text-xs truncate" style="color:var(--t3)">{{ b.direccion }}</p>
              <p class="font-mono text-xs mt-1" style="color:var(--t3)">{{ timeAgo(b.created_at) }}</p>
            </div>
            <div v-if="filtered.length === 0" class="text-center py-8 text-sm" style="color:var(--t3)">
              No hay eventos con esos filtros
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import { useTiposEvento } from '@/composables/useTiposEvento'
import api from '@/api'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()
const auth = useAuthStore()
const { theme, apply: applyTheme } = useTheme()
const { load: loadTipos, getTipo, buildMarkerHtml } = useTiposEvento()

const apiBase = import.meta.env.VITE_API_URL || ''
const bloqueos = ref([])
const selectedBloqueo = ref(null)
const newEventsCount = ref(0)
const showNewEventToast = ref(false)
let alertDismissTimer = null
const showMenu = ref(false)
const showMobileFilters = ref(false)
const menuRef = ref(null)

function dismissNewEventToast() {
  showNewEventToast.value = false
  if (alertDismissTimer) { clearTimeout(alertDismissTimer); alertDismissTimer = null }
}

function fmtDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString('es-GT', { dateStyle: 'short', timeStyle: 'short' })
}

const searchText = ref('')
const period = ref('all')
const estadoFilter = ref('Todos')
const tipoFilter = ref('')
const deptoFilter = ref('')
const sortBy = ref('newest')
const mapDark = ref(localStorage.getItem('mapTheme') === 'dark')

let map = null
let markers = {}
let tileLayer = null
let pollInterval = null

const DARK_TILE = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
const LIGHT_TILE = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

const periods = [
  { label: 'Hoy', value: 'today' },
  { label: 'Ayer', value: 'yesterday' },
  { label: '7 días', value: '7days' },
  { label: '30 días', value: '30days' },
  { label: 'Todos', value: 'all' },
]

const tiposUnicos = computed(() => [...new Set(bloqueos.value.map((b) => b.tipo_evento))].sort())
const deptosUnicos = computed(() => [...new Set(bloqueos.value.map((b) => b.departamento))].sort())
const activos = computed(() => bloqueos.value.filter((b) => b.estado === 'Activo').length)
const finalizados = computed(() => bloqueos.value.filter((b) => b.estado === 'Finalizado').length)

const tipoStats = computed(() => {
  const stats = {}
  bloqueos.value.forEach((b) => { stats[b.tipo_evento] = (stats[b.tipo_evento] || 0) + 1 })
  return Object.entries(stats).map(([tipo, count]) => ({ tipo, count })).sort((a, b) => b.count - a.count)
})

const topDeptos = computed(() => {
  const stats = {}
  bloqueos.value.forEach((b) => { stats[b.departamento] = (stats[b.departamento] || 0) + 1 })
  return Object.entries(stats).map(([nombre, count]) => ({ nombre, count })).sort((a, b) => b.count - a.count).slice(0, 5)
})

const filtered = computed(() => {
  let list = [...bloqueos.value]
  const now = new Date()

  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter((b) =>
      [b.tipo_evento, b.municipio, b.departamento, b.direccion].some((v) => v?.toLowerCase().includes(q))
    )
  }

  if (period.value !== 'all') {
    const today = new Date(); today.setHours(0, 0, 0, 0)
    list = list.filter((b) => {
      const d = new Date(b.created_at)
      if (period.value === 'today') return d >= today
      if (period.value === 'yesterday') {
        const y = new Date(today); y.setDate(y.getDate() - 1)
        return d >= y && d < today
      }
      if (period.value === '7days') return d >= new Date(now - 7 * 86400000)
      if (period.value === '30days') return d >= new Date(now - 30 * 86400000)
      return true
    })
  }

  if (estadoFilter.value !== 'Todos') list = list.filter((b) => b.estado === estadoFilter.value)
  if (tipoFilter.value) list = list.filter((b) => b.tipo_evento === tipoFilter.value)
  if (deptoFilter.value) list = list.filter((b) => b.departamento === deptoFilter.value)

  if (sortBy.value === 'newest') list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  else if (sortBy.value === 'oldest') list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  else if (sortBy.value === 'active') list.sort((a, b) => (a.estado === 'Activo' ? -1 : 1))

  return list
})

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

function clearFilters() {
  searchText.value = ''
  period.value = 'all'
  estadoFilter.value = 'Todos'
  tipoFilter.value = ''
  deptoFilter.value = ''
  sortBy.value = 'newest'
}

function logout() {
  auth.logout()
  router.push('/login')
}

function toggleMapTheme() {
  mapDark.value = !mapDark.value
  localStorage.setItem('mapTheme', mapDark.value ? 'dark' : 'light')
  if (tileLayer && map) {
    map.removeLayer(tileLayer)
    tileLayer = L.tileLayer(mapDark.value ? DARK_TILE : LIGHT_TILE, { maxZoom: 19, attribution: '' })
    tileLayer.addTo(map)
  }
}

function initMap() {
  map = L.map('welcome-map', {
    center: [14.6349, -90.5069],
    zoom: 7,
    zoomControl: false,
  })
  L.control.zoom({ position: 'bottomright' }).addTo(map)
  tileLayer = L.tileLayer(mapDark.value ? DARK_TILE : LIGHT_TILE, { maxZoom: 19, attribution: '' })
  tileLayer.addTo(map)
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
    if (markers[b.id]) {
      markers[b.id].setIcon(icon)
    } else {
      const m = L.marker([b.latitud, b.longitud], { icon })
      m.on('click', () => {
        selectedBloqueo.value = b
        map.setView([b.latitud, b.longitud], 14)
      })
      m.addTo(map)
      markers[b.id] = m
    }
  })
}

function focusEvent(b) {
  selectedBloqueo.value = b
  if (map) map.setView([b.latitud, b.longitud], 14)
}

async function fetchBloqueos() {
  try {
    const { data } = await api.get('/api/bloqueos')
    if (bloqueos.value.length > 0) {
      const knownIds = new Set(bloqueos.value.map((b) => b.id))
      const truly_new = data.filter((b) => !knownIds.has(b.id))
      if (truly_new.length > 0) {
        newEventsCount.value += truly_new.length
        showNewEventToast.value = true
        if (alertDismissTimer) clearTimeout(alertDismissTimer)
        alertDismissTimer = setTimeout(dismissNewEventToast, 5000)
      }
    }
    bloqueos.value = data
    renderMarkers(data)
  } catch {}
}

onMounted(async () => {
  await loadTipos()
  initMap()
  await fetchBloqueos()
  pollInterval = setInterval(fetchBloqueos, 10000)

  document.addEventListener('click', (e) => {
    if (menuRef.value && !menuRef.value.contains(e.target)) {
      showMenu.value = false
    }
  })
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  if (alertDismissTimer) clearTimeout(alertDismissTimer)
  if (map) map.remove()
})

watch(bloqueos, (list) => renderMarkers(list))
</script>

<style scoped>
/* Toast enter/leave transitions */
.event-toast-enter-active { transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) }
.event-toast-leave-active { transition: all 0.25s ease-in }
.event-toast-enter-from  { opacity: 0; transform: translateX(-50%) translateY(-16px) scale(0.9) }
.event-toast-leave-to    { opacity: 0; transform: translateX(-50%) translateY(-8px) scale(0.95) }

/* Progress bar shrinks from 100% to 0 in 5s */
.event-toast-progress {
  animation: toast-drain 5s linear forwards;
}
@keyframes toast-drain {
  from { width: 100% }
  to   { width: 0% }
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

@media (max-width: 640px) {
  .theme-switch button {
    min-width: 48px;
  }
}
</style>
