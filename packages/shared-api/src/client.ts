import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const BASE_URL = '/qingkong'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── 请求拦截器：自动带上 Token ─────────────────────
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── 响应拦截器：统一错误处理 ──────────────────────
apiClient.interceptors.response.use(
  (response) => response.data,  // 成功：直接返回 data，不用每次写 .data
  async (error: AxiosError<{ detail: string }>) => {
    const status = error.response?.status
    const message = error.response?.data?.detail ?? '请求失败，请稍后重试'

    // Token 过期，尝试用 refresh_token 换新 token
    if (status === 401) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post(`/qingkong/auth/refresh`, {
            refreshToken,
          })
          const newToken = res.data.accessToken
          localStorage.setItem('access_token', newToken)

          // 用新 token 重试原来的请求
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${newToken}`
            return apiClient(error.config)
          }
        }
        catch {
          // refresh 也失败了，清除登录状态
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(new Error(message))
  },
)
