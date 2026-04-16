export function useApi() {
  const config = useRuntimeConfig()
  const clientBase = config.public.apiBase as string
  const baseURL = import.meta.server
    ? 'http://127.0.0.1:8000/qingkong'
    : clientBase

  async function $get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    return await $fetch<T>(url, {
      baseURL,
      method: 'GET',
      params,
    })
  }

  return { $get }
}

export interface AuthorBrief {
  id: number
  username: string
  avatar: string | null
}

export interface CategoryBrief {
  id: number
  name: string
  slug: string
}

export interface TagBrief {
  id: number
  name: string
  slug: string
  color: string | null
}

export interface PostSummary {
  id: number
  title: string
  slug: string
  summary: string | null
  coverImage: string | null
  status: string
  viewCount: number
  likeCount: number
  createdAt: string
  updatedAt: string
  publishedAt: string | null
  author: AuthorBrief
  category: CategoryBrief | null
  tags: TagBrief[]
}

export interface PostDetail extends PostSummary {
  content: string | null
}

export interface PostListResponse {
  items: PostSummary[]
  total: number
  page: number
  pageSize: number
}

export interface CategoryNode {
  id: number
  name: string
  slug: string
  description: string | null
  parentId: number | null
  children: CategoryNode[]
}

export interface TagItem {
  id: number
  name: string
  slug: string
  color: string | null
}

export function usePostApi() {
  const { $get } = useApi()

  function list(params?: { page?: number; pageSize?: number; status?: string; categoryId?: number; tagId?: number; search?: string }) {
    return $get<PostListResponse>('/posts', params as Record<string, unknown>)
  }

  function getBySlug(slug: string) {
    return $get<PostDetail>(`/posts/slug/${slug}`)
  }

  return { list, getBySlug }
}

export function useCategoryApi() {
  const { $get } = useApi()

  function list() {
    return $get<CategoryNode[]>('/categories')
  }

  function getBySlug(slug: string) {
    return $get<CategoryNode>(`/categories/slug/${slug}`)
  }

  return { list, getBySlug }
}

export function useTagApi() {
  const { $get } = useApi()

  function list() {
    return $get<TagItem[]>('/tags')
  }

  function getBySlug(slug: string) {
    return $get<TagItem>(`/tags/slug/${slug}`)
  }

  return { list, getBySlug }
}
