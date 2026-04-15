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
  
  export interface Share {
    id: number
    fileId: number
    ownerId: number
    token: string
    password: string | null
    expireAt: string | null
    downloadCount: number
  }
  