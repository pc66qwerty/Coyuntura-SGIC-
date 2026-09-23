<template>
  <footer class="border-t border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50 py-6 mt-8">
    <div class="max-w-[1400px] mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-3 flex-wrap">
      <div class="flex items-center gap-2 text-gray-400 dark:text-gray-500 text-sm">
        <span><strong class="text-gray-500 dark:text-gray-400">Coyuntura SGIC</strong></span>
      </div>
      <div class="flex items-center gap-2.5 text-xs flex-wrap justify-center">
        <img src="/SGIC.png" alt="SGIC" class="h-5 w-auto object-contain opacity-70" @error="$event.target.style.display='none'"/>
        <span class="font-bold text-gray-400 dark:text-gray-600">SGIC</span>
        <span class="text-gray-200 dark:text-gray-700">·</span>
        <img src="/CRADIC.png" alt="CRADIC" class="h-5 w-auto object-contain opacity-70" @error="$event.target.style.display='none'"/>
        <span class="font-bold text-gray-400 dark:text-gray-600">CRADIC</span>
        <span class="text-gray-200 dark:text-gray-700">·</span>
        <img src="/SESIC.png" alt="SESIC" class="h-5 w-auto object-contain opacity-70" @error="$event.target.style.display='none'"/>
        <span class="font-bold text-gray-400 dark:text-gray-600">SESIC</span>
      </div>
      <div v-if="status" class="flex items-center gap-1.5 text-xs text-gray-300 dark:text-gray-600">
        <span class="relative flex h-1.5 w-1.5">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-50"></span>
          <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
        </span>
        {{ status }}
      </div>
    </div>
  </footer>
</template>

<script setup>
defineProps({
  status: { type: String, default: '' },
})
</script>
