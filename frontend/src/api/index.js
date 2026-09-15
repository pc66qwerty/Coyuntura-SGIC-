import axios from 'axios'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('mv_token')
      localStorage.removeItem('mv_user')
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default api
