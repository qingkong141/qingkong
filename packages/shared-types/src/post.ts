export type PostStatus = 'draft' | 'published' | 'archived'

export interface Category {
  id: number
  name: string
  slug: string
  description: string | null
  parentId: number | null
  children?: Category[]
}

export interface Tag {
  id: number
  name: string
  slug: string
  color: string | null
}

export interface Post {
  id: number
  title: string
  slug: string
  content: string | null
  summary: string | null
  coverImage: string | null
  authorId: number
  categoryId: number | null
  status: PostStatus
  viewCount: number
  likeCount: number
  createdAt: string
  updatedAt: string
  publishedAt: string | null
  // 关联数据（部分接口会返回）
  author?: Pick<import('./user').User, 'id' | 'username' | 'avatar'>
  category?: Category
  tags?: Tag[]
}

export interface Comment {
  id: number
  postId: number
  authorId: number
  parentId: number | null
  content: string
  status: 'pending' | 'approved'
  createdAt: string
  author?: Pick<import('./user').User, 'id' | 'username' | 'avatar'>
  replies?: Comment[]
}
