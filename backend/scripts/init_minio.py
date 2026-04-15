import json
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

# 设置公开读策略（avatars/ 目录下的文件可以直接访问）
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket}/avatars/*"],
        }
    ],
}
client.set_bucket_policy(bucket, json.dumps(policy))
print(f"Bucket '{bucket}' 公开读策略设置成功")
