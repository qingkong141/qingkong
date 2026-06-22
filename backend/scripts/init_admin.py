"""初始化管理员账户: admin / org@2022"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import hash_password


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        existing = result.scalar_one_or_none()

        if existing:
            existing.is_admin = True
            existing.is_approved = True
            await db.commit()
            print("✅ admin 账户已存在，已确保管理员权限")
            return

        admin = User(
            username="admin",
            email="admin@yunpan.local",
            password_hash=hash_password("org@2022"),
            is_admin=True,
            is_approved=True,
        )
        db.add(admin)
        await db.commit()
        print("✅ 管理员账户已创建: admin / org@2022")


if __name__ == "__main__":
    asyncio.run(main())
