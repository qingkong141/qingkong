# 青空 QingKong 部署指南

> 对应 `blog-drive-plan.md` 中 Phase 9（Session 48 ~ 50）

## 架构总览

```
                    Internet
                       │
                       ▼
            ┌──────── nginx :80 ────────┐
            │  (反代 + 静态资源服务)      │
            └──────────────┬─────────────┘
                           │
     ┌─────────────────────┼──────────────────────┐
     ▼                     ▼                      ▼
  Nuxt3 SSR           FastAPI :8000           MinIO :9000
  :3000               (REST API)              (对象存储)
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
              PostgreSQL          Redis
                 :5432             :6379
```

- **浏览器侧所有调用都同源**（通过 nginx 统一入口 `:80`）。
- 静态子应用（admin-shell / blog-admin / drive）全部内嵌进 nginx 镜像的 `/usr/share/nginx/html/`，以各自路径前缀提供。
- Nuxt 3 SSR 容器内直连 `backend:8000` 完成服务端渲染期的数据拉取。

## 路由表

| 路径前缀                 | 后端                                           |
|--------------------------|------------------------------------------------|
| `/`                      | Nuxt 3 博客前台（SSR，`nuxt-blog:3000`）        |
| `/admin`                 | admin-shell 静态（qiankun 主壳）                |
| `/login` `/s/:token`     | admin-shell 静态（主壳 SPA 路由）               |
| `/blog-admin/`           | blog-admin 静态（qiankun 子应用入口）           |
| `/drive/`                | drive 静态（qiankun 子应用入口）                |
| `/qingkong/*`            | FastAPI（`backend:8000`）                       |
| `/minio/*`（可选）       | MinIO 9000（若用公共签名 URL，可不开启）        |

## 一次性准备

```bash
cp .env.production.example .env.production

# 生成强密码（示例）
openssl rand -hex 48      # JWT_SECRET_KEY
openssl rand -base64 24   # POSTGRES_PASSWORD / REDIS_PASSWORD / MINIO_ROOT_PASSWORD

# 编辑 .env.production，替换所有 CHANGE_ME_* 值
```

## 构建与启动

```bash
# 构建三个自研镜像 + 启动全部服务
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  up -d --build

docker compose -f docker-compose.prod.yml ps
```

首次启动后，需在 backend 容器内执行一次数据库迁移与 MinIO bucket 初始化：

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml exec backend python scripts/init_minio.py
```

> 如果已有这两个脚本路径不同，请按实际项目结构调整。

## 日常运维

```bash
# 查看日志
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f backend

# 重启单个服务
docker compose -f docker-compose.prod.yml restart backend

# 仅重建前端（nginx 镜像内含 3 个静态子应用）
docker compose -f docker-compose.prod.yml build nginx && \
docker compose -f docker-compose.prod.yml up -d nginx

# 备份数据库
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup-$(date +%F).sql
```

## HTTPS（可选）

推荐方案：在 `nginx` 容器外前置一层 Caddy / Traefik / 宿主机 nginx 完成 Let's Encrypt 自动续签，
内部 `nginx` 容器保持 HTTP，仅监听内网。或在当前 nginx 上挂证书：

```yaml
# docker-compose.prod.yml 内 nginx 服务
volumes:
  - ./certs:/etc/nginx/certs:ro
ports:
  - "443:443"
```

并在 `nginx/nginx.conf` 增加 `listen 443 ssl;` 与 `ssl_certificate` 配置。

## 常见问题

- **qiankun 子应用加载 404**：检查 `apps/admin-shell/src/micro/apps.ts` 中生产 `entry` 是否与 nginx 的 `/blog-admin/` `/drive/` 路径一致。
- **SSR 页面拿不到数据**：确认 `nuxt-blog` 容器环境变量 `NUXT_API_INTERNAL=http://backend:8000/qingkong`，且 `backend` 已启动。
- **静态资源 404**：静态子应用的 Vite `base` 必须与 nginx location 前缀严格对应（`/admin/` / `/blog-admin/` / `/drive/`）。
- **上传大文件失败**：`client_max_body_size` 已放到 2 GB，若还不够，继续调大 nginx 与 FastAPI 的 body 限制。

## Session 50 — 上线前全链路冒烟测试

按顺序执行一遍，任何一步失败即阻塞发布。

- [ ] `docker compose -f docker-compose.prod.yml ps` 全部服务 `healthy`
- [ ] `curl -I http://<host>/` 返回 200，HTML 来自 Nuxt（含 `<title>青空`）
- [ ] `curl -I http://<host>/admin` 返回 200，HTML 来自 admin-shell
- [ ] `curl -I http://<host>/blog-admin/` 返回 200
- [ ] `curl -I http://<host>/drive/` 返回 200
- [ ] `curl http://<host>/qingkong/health` 返回 `{"status":"ok"}`
- [ ] 浏览器打开 `/admin` → 未登录自动跳 `/login`
- [ ] 注册 → 登录 → 进入后台主壳正常
- [ ] 切到 `/admin/blog` 子应用挂载成功，能新建/发布一篇 Markdown 文章
- [ ] 切到 `/admin/drive` 子应用挂载成功，上传一个 >50 MB 文件秒传/分片都 OK
- [ ] 为文件创建分享链接，退出登录后 `/s/:token` 仍可访问下载
- [ ] 博客前台 `/` 能看到刚发的文章；详情页 Markdown / 代码高亮 / KaTeX 正常
- [ ] 评论、点赞、标签筛选、搜索功能点过一遍
- [ ] 移动端 devtools 模拟 → 响应式布局无溢出
- [ ] 关掉浏览器再打开 → 登录态正常保持（refresh token 生效）
