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

// Handle responses and errors
api.interceptors.response.use(
  response => {
    // API Gateway wraps responses, so unwrap them
    if (response.data && response.data.status_code !== undefined && response.data.content !== undefined) {
      const statusCode = response.data.status_code
      
      // If API Gateway returned an error status code, throw it
      if (statusCode >= 400) {
        const error = new Error()
        let errorData = response.data.content
        try {
          if (typeof errorData === 'string') {
            errorData = JSON.parse(errorData)
          }
        } catch (e) {
          // Keep as is if not JSON
        }
        error.response = {
          status: statusCode,
          data: errorData,
          headers: response.data.headers || {}
        }
        return Promise.reject(error)
      }
      
      // Successful response - unwrap the content
      try {
        return {
          ...response,
          status: statusCode,
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
  error => {
    // If error doesn't have response structure, check if it's from API Gateway
    if (error.response && error.response.data && error.response.data.status_code !== undefined) {
      const statusCode = error.response.data.status_code
      let errorData = error.response.data.content
      try {
        if (typeof errorData === 'string') {
          errorData = JSON.parse(errorData)
        }
      } catch (e) {
        // Keep as is if not JSON
      }
      error.response.status = statusCode
      error.response.data = errorData
    }
    return Promise.reject(error)
  }
)

export default api
