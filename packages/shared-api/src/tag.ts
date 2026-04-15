import { apiClient } from './client'
import type { Tag } from '@qingkong/shared-types'

export const tagApi = {
  list() {
    return apiClient.get<never, Tag[]>('/tags')
  },

  create(data: { name: string; slug?: string; color?: string }) {
    return apiClient.post<never, Tag>('/tags', data)
  },

  update(id: number, data: { name?: string; slug?: string; color?: string }) {
    return apiClient.put<never, Tag>(`/tags/${id}`, data)
  },

  delete(id: number) {
    return apiClient.delete(`/tags/${id}`)
  },
}
