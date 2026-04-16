from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File as FastAPIFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.storage import get_presigned_url
from app.models.user import User
from app.schemas.file import FileResponse, CreateFolderRequest, RenameRequest, MoveRequest, MultipartInitRequest
from app.services import file as file_service

router = APIRouter(prefix="/files", tags=["云盘"])


@router.get("", response_model=list[FileResponse])
async def list_files(
    parent_id: int | None = Query(default=None, alias="parentId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await file_service.list_files(parent_id, current_user.id, db)


@router.post("/folder", response_model=FileResponse, status_code=201)
async def create_folder(
    data: CreateFolderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await file_service.create_folder(data.name, data.parent_id, current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{file_id}/rename", response_model=FileResponse)
async def rename_file(
    file_id: int,
    data: RenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await file_service.rename_file(file_id, data.name, current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="文件不存在")
    return result


@router.put("/{file_id}/move", response_model=FileResponse)
async def move_file(
    file_id: int,
    data: MoveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await file_service.move_file(file_id, data.parent_id, current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="文件不存在")
    return result


@router.post("/upload", status_code=201)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    parent_id: int | None = Query(default=None, alias="parentId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    max_size = 100 * 1024 * 1024  # 100 MB
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail="文件大小不能超过 100MB，请使用分片上传")

    try:
        file_record, is_instant = await file_service.upload_file(
            filename=file.filename or "unnamed",
            content=content,
            content_type=file.content_type or "application/octet-stream",
            parent_id=parent_id,
            owner_id=current_user.id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        status_code=201,
        content={
            "id": file_record.id,
            "name": file_record.name,
            "size": file_record.size,
            "mimeType": file_record.mime_type,
            "isInstant": is_instant,
        },
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file_record = await file_service.get_file(file_id, current_user.id, db)
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    if file_record.is_dir:
        raise HTTPException(status_code=400, detail="不能下载文件夹")
    if not file_record.storage_key:
        raise HTTPException(status_code=404, detail="文件存储异常")

    url = get_presigned_url(file_record.storage_key)
    return {"url": url, "name": file_record.name}


@router.post("/multipart/init", status_code=201)
async def multipart_init(
    data: MultipartInitRequest,
    current_user: User = Depends(get_current_user),
):
    upload_id = await file_service.init_multipart(
        filename=data.filename,
        total_size=data.total_size,
        total_chunks=data.total_chunks,
        parent_id=data.parent_id,
        owner_id=current_user.id,
    )
    return {"uploadId": upload_id}


@router.post("/multipart/{upload_id}/chunk")
async def multipart_upload_chunk(
    upload_id: str,
    chunk_index: int = Query(..., alias="chunkIndex"),
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
):
    data = await file.read()
    try:
        result = await file_service.upload_chunk(upload_id, chunk_index, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.post("/multipart/{upload_id}/complete", status_code=201)
async def multipart_complete(
    upload_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        file_record, is_instant = await file_service.complete_multipart(
            upload_id, current_user.id, db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        status_code=201,
        content={
            "id": file_record.id,
            "name": file_record.name,
            "size": file_record.size,
            "mimeType": file_record.mime_type,
            "isInstant": is_instant,
        },
    )


@router.get("/trash", response_model=list[FileResponse])
async def list_trash(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await file_service.list_trash(current_user.id, db)


@router.post("/trash/{file_id}/restore", response_model=FileResponse)
async def restore_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await file_service.restore_file(file_id, current_user.id, db)
    if not result:
        raise HTTPException(status_code=404, detail="文件不存在")
    return result


@router.delete("/trash/{file_id}/permanent", status_code=204)
async def permanent_delete(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await file_service.permanent_delete(file_id, current_user.id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.delete("/trash", status_code=200)
async def empty_trash(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await file_service.empty_trash(current_user.id, db)
    return {"deleted": count}


@router.get("/storage/usage")
async def storage_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await file_service.get_storage_usage(current_user.id, db)


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await file_service.delete_file(file_id, current_user.id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="文件不存在")
