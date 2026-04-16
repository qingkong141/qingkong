import { apiClient } from './client'
import type { Comment, PaginatedResponse } from '@qingkong/shared-types'

export interface CommentWithPost extends Comment {
  postTitle: string | null
}

export interface CommentListParams {
  page?: number
  pageSize?: number
  status?: string
  postId?: number
  search?: string
}

export const commentApi = {
  list(params?: CommentListParams) {
    return apiClient.get<never, PaginatedResponse<CommentWithPost>>('/comments', { params })
  },

  updateStatus(id: number, status: 'pending' | 'approved') {
    return apiClient.put<never, CommentWithPost>(`/comments/${id}/status`, { status })
  },

  delete(id: number) {
    return apiClient.delete(`/comments/${id}`)
  },
}
