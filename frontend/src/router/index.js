import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login',          component: () => import('@/views/auth/Login.vue'),         meta: { guest: true } },
  { path: '/register',       redirect: '/login' },
  { path: '/forgot-password',component: () => import('@/views/auth/ForgotPassword.vue'),meta: { guest: true } },
  { path: '/terminos',       component: () => import('@/views/Terms.vue'),              meta: { requiresAuth: true } },
  { path: '/',               component: () => import('@/views/Welcome.vue'),            meta: { requiresAuth: true, requiresTerms: true } },
  { path: '/dashboard',      component: () => import('@/views/Dashboard.vue'),          meta: { requiresAuth: true, requiresTerms: true, requiresEditor: true } },
  { path: '/usuarios',       component: () => import('@/views/Users.vue'),              meta: { requiresAuth: true, requiresTerms: true, requiresEditor: true } },
  { path: '/tipos-evento',   component: () => import('@/views/TiposEvento.vue'),        meta: { requiresAuth: true, requiresTerms: true, requiresEditor: true } },
  { path: '/ayuda',          component: () => import('@/views/Ayuda.vue'),              meta: { requiresAuth: true, requiresTerms: true } },
  { path: '/:pathMatch(.*)*',redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  auth.init()

  if (to.meta.guest && auth.isAuthenticated) {
    return auth.hasAcceptedTerms ? '/' : '/terminos'
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'
  }
  if (to.meta.requiresTerms && auth.isAuthenticated && !auth.hasAcceptedTerms) {
    return '/terminos'
  }
  if (to.meta.requiresEditor && !auth.isEditor) {
    return '/'
  }
})

export default router
