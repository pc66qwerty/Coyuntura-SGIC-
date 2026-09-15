import { ref } from 'vue'

const theme = ref(localStorage.getItem('uiTheme') || 'light')

// Apply initial theme on module load
;(function () {
  if (theme.value === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})()

export function useTheme() {
  function apply(t) {
    if (t === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('uiTheme', t)
    theme.value = t
  }

  return { theme, apply }
}
