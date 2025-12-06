import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => Promise.reject(error))

// Handle errors
api.interceptors.response.use(
  response => {
    // API Gateway wraps responses, so unwrap them
    if (response.data.content && response.data.status_code) {
      try {
        return {
          ...response,
          data: typeof response.data.content === 'string' 
            ? JSON.parse(response.data.content) 
            : response.data.content
        }
      } catch (e) {
        return response
      }
    }
    return response
  },
  error => Promise.reject(error)
)

export default api
