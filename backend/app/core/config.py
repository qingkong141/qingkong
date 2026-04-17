from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # 数据库
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # MinIO
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 应用
    DEBUG: bool = False

    # 防呆：关键秘钥不能为空（compose 忘了 --env-file 时会直接拒绝启动）
    @field_validator("SECRET_KEY", "MINIO_BUCKET")
    @classmethod
    def _not_blank(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(
                f"环境变量 {info.field_name} 未正确加载（为空字符串）。"
                "请确认容器启动时 --env-file 已指向 .env.production，"
                "或本机 backend/.env 中该项已配置。"
            )
        return v


settings = Settings()
