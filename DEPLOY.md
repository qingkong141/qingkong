# 臻橙云盘 部署指南

## 架构总览

```
                   Internet
                      │
                      ▼
           ┌─── nginx :3847 ───────┐
           │  (反代 + 静态资源)      │
           └───────────┬────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    ▼                  ▼                  ▼
 admin-shell       FastAPI :8000      MinIO :9000
 drive 静态         (REST API)         (对象存储)
                       │
              ┌────────┴────────┐
              ▼                 ▼
          PostgreSQL          Redis
             :5432             :6379
```

- **所有浏览器请求同源**：统一通过 nginx `:3847` 入口
- **admin-shell + drive 静态文件**：内嵌在 nginx 镜像的 `/usr/share/nginx/html/`
- **API 路径**：`/yunpan/*` 反代到 FastAPI

## 路由表

| 路径 | 目标 |
|------|------|
| `/` | 302 → `/admin` |
| `/admin` | admin-shell 静态（qiankun 主壳） |
| `/login` `/s/:token` | admin-shell SPA 路由 |
| `/drive/` | drive 静态（qiankun 子应用） |
| `/yunpan/*` | FastAPI 后端 |
| `/minio/*`（可选） | MinIO 直连 |

## 前置准备

```bash
cp .env.production.example .env.production

# 生成强密码
openssl rand -hex 48      # JWT SECRET_KEY
openssl rand -base64 24   # POSTGRES_PASSWORD / REDIS_PASSWORD / MINIO_ROOT_PASSWORD

# 编辑 .env.production，替换所有 CHANGE_ME_* 值
```

## 构建与启动

```bash
# 构建镜像 + 启动全部服务
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  up -d --build

# 确认服务状态
docker compose -f docker-compose.prod.yml ps
```

## 首次初始化

```bash
# 执行数据库迁移
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 初始化 MinIO bucket
docker compose -f docker-compose.prod.yml exec backend python scripts/init_minio.py
```

## 访问

- 管理台：`http://<服务器IP>:3847/admin`
- API 文档：`http://<服务器IP>:3847/yunpan/docs`
- 健康检查：`http://<服务器IP>:3847/yunpan/health`

## 日常运维

```bash
# 查看日志
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f backend

# 重启单个服务
docker compose -f docker-compose.prod.yml restart backend

# 仅重建前端
docker compose -f docker-compose.prod.yml build nginx && \
docker compose -f docker-compose.prod.yml up -d nginx

# 备份数据库
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup-$(date +%F).sql
```

## HTTPS（可选）

前置一层 Caddy 或宿主机 nginx 做 SSL 终止，内部容器保持 HTTP。

```yaml
# docker-compose.prod.yml nginx 服务内
ports:
  - "3847:80"
  # 如需直接挂证书：
  # - "443:443"
```

## 冒烟测试清单

上线前逐项检查：

- [ ] `docker compose ps` 全部服务 `healthy`
- [ ] `curl http://<host>:3847/yunpan/health` → `{"status":"ok"}`
- [ ] 浏览器打开 `/admin` → 未登录跳 `/login`
- [ ] 注册 → 登录 → 进入管理台
- [ ] `/admin/drive` 子应用正常挂载
- [ ] 上传文件 → 分片上传 / 秒传正常
- [ ] 创建分享链接 → 无密码 / 有密码均可访问
- [ ] 分享页视频/音频/图片/PDF 预览正常
- [ ] 禁止下载时无法获取原始文件
- [ ] 移动端分享页正常显示和播放
- [ ] 关闭浏览器再打开 → 登录态保持（refresh token）

## 环境变量参考

| 变量 | 说明 |
|------|------|
| `POSTGRES_DB` | 数据库名 |
| `POSTGRES_USER` | 数据库用户 |
| `POSTGRES_PASSWORD` | 数据库密码 |
| `REDIS_PASSWORD` | Redis 密码 |
| `SECRET_KEY` | JWT 签名密钥 |
| `MINIO_ROOT_USER` | MinIO 用户名 |
| `MINIO_ROOT_PASSWORD` | MinIO 密码 |
| `DATABASE_URL` | 数据库连接串 |
| `REDIS_URL` | Redis 连接串 |
| `MINIO_ENDPOINT` | MinIO 地址 |
| `MINIO_ACCESS_KEY` | MinIO Access Key |
| `MINIO_SECRET_KEY` | MinIO Secret Key |
| `MINIO_BUCKET` | MinIO 桶名 |
