# 臻橙云盘 部署指南

## 架构总览

```
                   Internet
                      │
                      ▼   :3847（唯一对外端口）
           ┌─── nginx ──────────┐
           │  (反代 + 静态资源)   │
           └──────┬──────────────┘
                  │ Docker 内网
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
 admin-shell   backend:8912   MinIO:9000
 drive 静态     (FastAPI)     (对象存储)
                  │
         ┌────────┴────────┐
         ▼                 ▼
     PostgreSQL:5432    Redis:6379
```

**关键**：只有 nginx 的 3847 端口对外，其余所有服务都在 Docker 内网通信，外部无法直接访问。

## 端口说明

| 端口 | 用途 | 对外 |
|------|------|------|
| 3847 | nginx 统一入口 | ✅ 唯一对外 |
| 8912 | FastAPI 后端 | ❌ 仅 Docker 内网 |
| 5432 | PostgreSQL | ❌ 仅 Docker 内网 |
| 6379 | Redis | ❌ 仅 Docker 内网 |
| 9000 | MinIO API | ❌ 仅 Docker 内网 |
| 9001 | MinIO 控制台 | ❌ 仅 Docker 内网 |

---

## 一、发布前检测清单

每次发布前在本机执行：

```bash
# 1. 后端语法检查
cd backend && python -c "from app.main import app; print('OK')"

# 2. 前端构建检查（确保不报错）
pnpm install
pnpm build

# 3. 确认所有迁移文件存在
ls backend/alembic/versions/*.py

# 4. 确认脚本就绪
ls backend/scripts/init_admin.py
ls backend/scripts/recalc_storage.py

# 5. 确认环境变量模板完整
cat backend/.env
```

---

## 二、首次发布

### 1. 准备 .env

```bash
# 在服务器上
cp .env.template .env
vim .env
```

必填项（生成强密码）：

```bash
SECRET_KEY=<openssl rand -hex 48>
POSTGRES_PASSWORD=<openssl rand -base64 24>
REDIS_PASSWORD=<openssl rand -base64 24>
MINIO_SECRET_KEY=<openssl rand -base64 24>
```

### 2. 构建并启动

```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

### 3. 初始化

```bash
# 数据库迁移
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 创建管理员 admin / org@2022
docker compose -f docker-compose.prod.yml exec backend python scripts/init_admin.py
```

### 4. 验证

```bash
# 健康检查
curl http://localhost:3847/yunpan/health
# → {"status":"ok"}

# 确认管理台可访问
curl -I http://localhost:3847/admin
# → 200
```

浏览器打开 `http://<服务器IP>:3847/admin`，用 `admin / org@2022` 登录，首次登录后立即修改密码。

---

## 三、迭代发布

每次发布只需要更新变化的服务：

```bash
# 拉取最新代码
git pull

# 只构建需要更新的镜像（例如 backend 或 nginx）
docker compose --env-file .env -f docker-compose.prod.yml up -d --build backend
docker compose --env-file .env -f docker-compose.prod.yml up -d --build nginx

# 如果有新的数据库迁移
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 重启受影响的服务
docker compose -f docker-compose.prod.yml restart backend
```

**无停机更新**（推荐生产环境）：
```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d --build --scale backend=2 backend
docker compose --env-file .env -f docker-compose.prod.yml up -d --build nginx
```

---

## 四、常见运维

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f --tail=100 backend
docker compose -f docker-compose.prod.yml logs -f --tail=100 nginx

# 重启单个服务
docker compose -f docker-compose.prod.yml restart backend

# 备份数据库
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U yunpan yunpan > backup-$(date +%F).sql
```

## 五、HTTPS（可选）

前置一层 Caddy 或宿主机 nginx 做 SSL 终止：

```yaml
# 把 nginx 的 ports 改为只监听内网
# 前面加 caddy 容器：
caddy:
  image: caddy:2-alpine
  ports:
    - "443:443"
  volumes:
    - ./Caddyfile:/etc/caddy/Caddyfile:ro
```

---

## 六、环境变量参考

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | 数据库连接 | `postgresql+asyncpg://yunpan:pass@postgres:5432/yunpan` |
| `REDIS_URL` | Redis 连接 | `redis://:pass@redis:6379/0` |
| `MINIO_ENDPOINT` | MinIO 地址 | `minio:9000` |
| `MINIO_ACCESS_KEY` | MinIO 用户名 | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO 密码 | `<强密码>` |
| `MINIO_BUCKET` | 存储桶名 | `yunpan` |
| `SECRET_KEY` | JWT 密钥 | `<openssl rand -hex 48>` |
| `POSTGRES_DB` | 数据库名 | `yunpan` |
| `POSTGRES_USER` | 数据库用户 | `yunpan` |
| `POSTGRES_PASSWORD` | 数据库密码 | `<强密码>` |
| `REDIS_PASSWORD` | Redis 密码 | `<强密码>` |
| `PORT` | nginx 对外端口 | `3847` |
