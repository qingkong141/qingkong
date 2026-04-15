// 分页请求参数
export interface PaginationQuery {
    page?: number
    pageSize?: number
  }
  
  // 分页响应格式
  export interface PaginatedResponse<T> {
    items: T[]
    total: number
    page: number
    pageSize: number
  }
  
  // 通用 API 响应格式
  export interface ApiResponse<T = null> {
    data: T
    detail?: string
  }
  