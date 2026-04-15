import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@qingkong/shared-api'
import type { User, LoginRequest } from '@qingkong/shared-types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isLoggedIn = () => !!accessToken.value

  async function login(data: LoginRequest) {
    const res = await authApi.login(data)
    accessToken.value = res.accessToken
    refreshToken.value = res.refreshToken
    localStorage.setItem('access_token', res.accessToken)
    localStorage.setItem('refresh_token', res.refreshToken)
  }

  async function fetchUser() {
    user.value = await authApi.me()
  }

  async function logout() {
    if (refreshToken.value) {
      await authApi.logout(refreshToken.value).catch(() => {})
    }
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, isLoggedIn, login, fetchUser, logout }
})
