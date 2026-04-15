import { apiClient } from './client'
import type { Category } from '@qingkong/shared-types'

export const categoryApi = {
  list() {
    return apiClient.get<never, Category[]>('/categories')
  },

  create(data: { name: string; slug?: string; description?: string; parentId?: number }) {
    return apiClient.post<never, { id: number; name: string; slug: string }>('/categories', data)
  },

  update(id: number, data: { name?: string; slug?: string; description?: string }) {
    return apiClient.put<never, { id: number; name: string; slug: string }>(`/categories/${id}`, data)
  },

  delete(id: number) {
    return apiClient.delete(`/categories/${id}`)
  },
}
