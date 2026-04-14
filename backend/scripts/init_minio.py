from minio import Minio
from app.core.config import settings

client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)

bucket = settings.MINIO_BUCKET

if not client.bucket_exists(bucket):
    client.make_bucket(bucket)
    print(f"Bucket '{bucket}' 创建成功")
else:
    print(f"Bucket '{bucket}' 已存在")
