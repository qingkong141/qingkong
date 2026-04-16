import { apiClient } from './client'

export interface FileItem {
  id: number
  name: string
  path: string
  parentId: number | null
  size: number
  mimeType: string | null
  storageKey: string | null
  md5: string | null
  ownerId: number
  isDir: boolean
  isDeleted: boolean
  createdAt: string
  updatedAt: string
}

export interface ShareItem {
  id: number
  fileId: number
  token: string
  hasPassword: boolean
  expireAt: string | null
  downloadCount: number
  createdAt: string
  fileName: string
  fileSize: number
  isDir: boolean
}

export interface StorageUsage {
  used: number
  quota: number
  usedFormatted: string
  quotaFormatted: string
  percentage: number
}

export const fileApi = {
  list(parentId?: number | null) {
    const params: Record<string, any> = {}
    if (parentId != null) params.parentId = parentId
    return apiClient.get<any, FileItem[]>('/files', { params })
  },

  createFolder(name: string, parentId?: number | null) {
    return apiClient.post<any, FileItem>('/files/folder', { name, parentId })
  },

  rename(fileId: number, name: string) {
    return apiClient.put<any, FileItem>(`/files/${fileId}/rename`, { name })
  },

  move(fileId: number, parentId: number | null) {
    return apiClient.put<any, FileItem>(`/files/${fileId}/move`, { parentId })
  },

  delete(fileId: number) {
    return apiClient.delete(`/files/${fileId}`)
  },

  upload(file: File, parentId?: number | null, onProgress?: (pct: number) => void) {
    const form = new FormData()
    form.append('file', file)
    const params: Record<string, any> = {}
    if (parentId != null) params.parentId = parentId
    return apiClient.post<any, { id: number; name: string; size: number; mimeType: string; isInstant: boolean }>(
      '/files/upload',
      form,
      {
        params,
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 0,
        onUploadProgress(e) {
          if (e.total && onProgress) onProgress(Math.round((e.loaded / e.total) * 100))
        },
      },
    )
  },

  download(fileId: number) {
    return apiClient.get<any, { url: string; name: string }>(`/files/${fileId}/download`)
  },

  multipartInit(filename: string, totalSize: number, totalChunks: number, parentId?: number | null) {
    return apiClient.post<any, { uploadId: string }>('/files/multipart/init', {
      filename, totalSize, totalChunks, parentId,
    })
  },

  multipartChunk(uploadId: string, chunkIndex: number, chunk: Blob) {
    const form = new FormData()
    form.append('file', chunk)
    return apiClient.post<any, { chunkIndex: number; uploaded: number; total: number }>(
      `/files/multipart/${uploadId}/chunk`,
      form,
      {
        params: { chunkIndex },
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 0,
      },
    )
  },

  multipartComplete(uploadId: string) {
    return apiClient.post<any, { id: number; name: string; size: number; mimeType: string; isInstant: boolean }>(
      `/files/multipart/${uploadId}/complete`,
    )
  },

  listTrash() {
    return apiClient.get<any, FileItem[]>('/files/trash')
  },

  restore(fileId: number) {
    return apiClient.post<any, FileItem>(`/files/trash/${fileId}/restore`)
  },

  permanentDelete(fileId: number) {
    return apiClient.delete(`/files/trash/${fileId}/permanent`)
  },

  emptyTrash() {
    return apiClient.delete<any, { deleted: number }>('/files/trash')
  },

  storageUsage() {
    return apiClient.get<any, StorageUsage>('/files/storage/usage')
  },
}

export const shareApi = {
  create(fileId: number, password?: string | null, expireHours?: number | null) {
    return apiClient.post<any, ShareItem>('/shares', { fileId, password, expireHours })
  },

  list() {
    return apiClient.get<any, ShareItem[]>('/shares')
  },

  delete(shareId: number) {
    return apiClient.delete(`/shares/${shareId}`)
  },
}
