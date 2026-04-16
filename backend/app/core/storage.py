from io import BytesIO
from minio import Minio
from minio.error import S3Error

from app.core.config import settings

_client: Minio | None = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )
        if not _client.bucket_exists(settings.MINIO_BUCKET):
            _client.make_bucket(settings.MINIO_BUCKET)
    return _client


def upload_to_minio(key: str, data: bytes, content_type: str) -> str:
    client = get_minio_client()
    client.put_object(
        settings.MINIO_BUCKET,
        key,
        BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return key


def upload_stream_to_minio(key: str, stream: BytesIO, length: int, content_type: str) -> str:
    client = get_minio_client()
    client.put_object(
        settings.MINIO_BUCKET,
        key,
        stream,
        length=length,
        content_type=content_type,
    )
    return key


def delete_from_minio(key: str):
    client = get_minio_client()
    try:
        client.remove_object(settings.MINIO_BUCKET, key)
    except S3Error:
        pass


def get_presigned_url(key: str, expires_seconds: int = 600) -> str:
    from datetime import timedelta
    client = get_minio_client()
    return client.presigned_get_object(
        settings.MINIO_BUCKET,
        key,
        expires=timedelta(seconds=expires_seconds),
    )
