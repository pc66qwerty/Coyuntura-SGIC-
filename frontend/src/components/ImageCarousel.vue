<template>
  <div v-if="images.length" class="relative select-none rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700 bg-black/5"
    @mouseenter="paused = true" @mouseleave="paused = false"
    @touchstart="onTouchStart" @touchend="onTouchEnd">
    <div class="flex transition-transform duration-[400ms] ease-out" :style="`transform:translateX(-${index * 100}%)`">
      <img v-for="(src, i) in images" :key="src + i" :src="src" :alt="`Foto ${i + 1}`"
        class="w-full object-cover flex-shrink-0" :style="`height:${height}`" draggable="false" />
    </div>

    <template v-if="images.length > 1">
      <button type="button" @click.stop="prev"
        class="absolute left-1.5 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full flex items-center justify-center bg-black/40 hover:bg-black/60 text-white transition">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <button type="button" @click.stop="next"
        class="absolute right-1.5 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full flex items-center justify-center bg-black/40 hover:bg-black/60 text-white transition">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
        </svg>
      </button>

      <div class="absolute top-2 right-2 px-1.5 py-0.5 rounded-full bg-black/50 text-white text-[10px] font-mono">
        {{ index + 1 }}/{{ images.length }}
      </div>

      <div class="absolute bottom-1.5 left-1/2 -translate-x-1/2 flex items-center gap-1.5">
        <button v-for="(src, i) in images" :key="'dot' + i" type="button" @click.stop="go(i)"
          class="rounded-full transition-all"
          :class="i === index ? 'w-4 h-1.5 bg-white' : 'w-1.5 h-1.5 bg-white/50 hover:bg-white/80'">
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  images: { type: Array, default: () => [] },
  height: { type: String, default: '160px' },
  autoplay: { type: Boolean, default: true },
  interval: { type: Number, default: 4000 },
})

const index = ref(0)
const paused = ref(false)
let timer = null
let touchStartX = 0

function go(i) {
  if (!props.images.length) return
  index.value = ((i % props.images.length) + props.images.length) % props.images.length
}
function next() { go(index.value + 1) }
function prev() { go(index.value - 1) }

function onTouchStart(e) { touchStartX = e.changedTouches[0].clientX }
function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - touchStartX
  if (dx > 40) prev()
  else if (dx < -40) next()
}

function startAutoplay() {
  clearInterval(timer)
  if (!props.autoplay || props.images.length < 2) return
  timer = setInterval(() => { if (!paused.value) next() }, props.interval)
}

watch(() => props.images, () => { index.value = 0; startAutoplay() })

onMounted(startAutoplay)
onUnmounted(() => clearInterval(timer))
</script>
