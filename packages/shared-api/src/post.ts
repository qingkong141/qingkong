import { apiClient } from './client'
import type { Post, PaginatedResponse } from '@qingkong/shared-types'

export interface PostListParams {
  page?: number
  pageSize?: number
  status?: string
  categoryId?: number
  tagId?: number
  search?: string
}

export interface CreatePostBody {
  title: string
  content?: string
  summary?: string
  coverImage?: string
  categoryId?: number
  tagIds?: number[]
  status?: 'draft' | 'published'
}

export type UpdatePostBody = Partial<CreatePostBody>

export const postApi = {
  list(params?: PostListParams) {
    return apiClient.get<never, PaginatedResponse<Post>>('/posts', { params })
  },

  get(id: number) {
    return apiClient.get<never, Post>(`/posts/${id}`)
  },

  create(data: CreatePostBody) {
    return apiClient.post<never, Post>('/posts', data)
  },

  update(id: number, data: UpdatePostBody) {
    return apiClient.put<never, Post>(`/posts/${id}`, data)
  },

  delete(id: number) {
    return apiClient.delete(`/posts/${id}`)
  },
}
