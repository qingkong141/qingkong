import { apiClient } from './client'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  ChangePasswordRequest,
} from '@yunpan/shared-types'

export const authApi = {
  // 注册
  register(data: RegisterRequest) {
    return apiClient.post<never, { id: number; username: string; email: string }>(
      '/auth/register',
      data,
    )
  },

  // 登录
  login(data: LoginRequest) {
    return apiClient.post<never, TokenResponse>('/auth/login', data)
  },

  // 刷新 token
  refresh(refreshToken: string) {
    return apiClient.post<never, Pick<TokenResponse, 'accessToken' | 'tokenType'>>(
      '/auth/refresh',
      { refreshToken },
    )
  },

  // 注销
  logout(refreshToken: string) {
    return apiClient.post('/auth/logout', { refreshToken })
  },

  // 当前用户信息
  me() {
    return apiClient.get<never, User>('/auth/me')
  },

  // 修改密码
  changePassword(data: ChangePasswordRequest) {
    return apiClient.put('/auth/password', data)
  },

  // 上传头像
  uploadAvatar(file: File) {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post<never, { avatar: string }>('/auth/avatar', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // ── 管理员 ──
  adminListUsers(status?: string) {
    return apiClient.get<any, any[]>('/auth/admin/users', { params: status ? { status } : {} })
  },
  adminApproveUser(userId: number) {
    return apiClient.put<any, any>(`/auth/admin/users/${userId}/approve`)
  },
  adminDeleteUser(userId: number) {
    return apiClient.delete(`/auth/admin/users/${userId}`)
  },
  adminDisableUser(userId: number) {
    return apiClient.put<any, any>(`/auth/admin/users/${userId}/disable`)
  },
  adminSetQuota(userId: number, quotaGb: number) {
    return apiClient.put<any, any>(`/auth/admin/users/${userId}/quota`, null, { params: { quota_gb: quotaGb } })
  },
}
