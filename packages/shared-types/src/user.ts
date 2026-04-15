export interface User {
    id: number
    username: string
    email: string
    avatar: string | null
    bio: string | null
    storageUsed: number
    storageQuota: number
    createdAt: string
    updatedAt: string
  }
  
  export interface LoginRequest {
    email: string
    password: string
  }
  
  export interface RegisterRequest {
    username: string
    email: string
    password: string
  }
  
  export interface TokenResponse {
    accessToken: string
    refreshToken: string
    tokenType: string
  }
  
  export interface ChangePasswordRequest {
    oldPassword: string
    newPassword: string
  }
  