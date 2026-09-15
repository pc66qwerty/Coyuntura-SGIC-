import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('mv_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('mv_user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isEditor = computed(() => user.value?.role === 'editor')
  const hasAcceptedTerms = computed(() => user.value?.terms_accepted === true)

  function setAuth(data) {
    token.value = data.token
    user.value = data.user
    localStorage.setItem('mv_token', data.token)
    localStorage.setItem('mv_user', JSON.stringify(data.user))
    api.defaults.headers.common['Authorization'] = `Bearer ${data.token}`
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('mv_token')
    localStorage.removeItem('mv_user')
    delete api.defaults.headers.common['Authorization']
  }

  function init() {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  return { token, user, isAuthenticated, isEditor, hasAcceptedTerms, setAuth, logout, init }
})
