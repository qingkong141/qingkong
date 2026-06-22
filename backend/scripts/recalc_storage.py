"""重新计算所有用户的 storage_used"""
import asyncio
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.file import File


async def main():
    async with AsyncSessionLocal() as db:
        # 查所有用户
        result = await db.execute(select(User))
        users = result.scalars().all()

        for user in users:
            # 统计该用户非目录、未删除文件的总大小
            total = await db.execute(
                select(func.coalesce(func.sum(File.size), 0))
                .where(
                    File.owner_id == user.id,
                    File.is_dir == False,
                    File.is_deleted == False,
                )
            )
            used = total.scalar()
            if user.storage_used != used:
                print(f"  {user.username}: {user.storage_used} -> {used} ({used / (1024**3):.2f} GB)")
                user.storage_used = used

        await db.commit()
        print("✅ 存储用量已重新计算")


if __name__ == "__main__":
    asyncio.run(main())
