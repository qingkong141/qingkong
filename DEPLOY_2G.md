# 臻橙云盘 2G 服务器精简部署方案

> 把吃内存的「数据库 + 对象存储」搬到云端托管，只在 2G 小机器上跑应用层。
> 自用场景，目标：稳定、便宜、不折腾。

---

## 一、核心思路

### 默认架构 vs 2G 精简架构

| 组件 | 默认（[docker-compose.prod.yml](docker-compose.prod.yml)） | 2G 精简方案 |
|------|-------------------------|------------|
| PostgreSQL | 本机容器 ~200MB | **外置云数据库** |
| MinIO | 本机容器 ~250MB + 数据盘 | **外置 S3 兼容对象存储** |
| Redis | 本机容器 ~50MB | **保留本机**（小，没必要外置） |
| FastAPI backend | 本机容器 ~200MB | 保留 |
| Nginx | 本机容器 ~30MB | 保留（含 admin-shell + drive 静态文件） |

### 内存预算（2GB 服务器）

```
OS（Ubuntu）          400 MB
Docker daemon          100 MB
Redis                   50 MB
Backend (FastAPI)      200 MB
Nginx                   30 MB
─────────────────────────────
已用                  ~780 MB
剩余可用             ~1228 MB   ← 留给突发流量、构建、buff/cache
```

舒服很多。原方案 2G 跑全栈基本一启动就 OOM。

---

## 二、云资源选型

下面给两条路径，根据你是否准备**备案**来选：

### 路径 A：全国内（已备案 / 计划备案）

| 组件 | 推荐 | 价格参考 |
|------|------|----------|
| 云数据库 PostgreSQL | 腾讯云轻量数据库 1核1G | ~¥30/月 |
| 对象存储 | 阿里云 OSS / 腾讯云 COS（按量） | 0.12 元/GB/月 + 流量费 |
| 服务器 | 腾讯云轻量 2核2G 6M | ~¥90/年（首年）|
| **合计** | | **约 ¥40-50/月** |

> 国内访问快，但所有云服务都需要实名 + 域名备案。

### 路径 B：海外免备案（推荐自用党）

| 组件 | 推荐 | 价格 |
|------|------|------|
| 云数据库 PostgreSQL | **Neon** [neon.tech](https://neon.tech) | **免费 0.5GB**，足够博客自用 |
| 对象存储 | **Cloudflare R2** [r2 dev](https://developers.cloudflare.com/r2/) | **免费 10GB + 零出口费** |
| 服务器 | 腾讯云轻量香港 2核2G 30M | ~¥288/年 |
| **合计** | | **约 ¥24/月**（基本只交服务器钱） |

**强烈推荐路径 B**：
- Neon 免费档稳定够用（免费 5GB 流量/月、autosuspend 节省资源）
- Cloudflare R2 没有"出网流量费"这个大坑（OSS/COS 都有）
- 不用备案，今天买明天就上线

下面所有步骤以**路径 B** 为主（路径 A 我会在差异点单独说明）。

---

## 三、代码改动清单

好消息：项目用的是 `minio-py` SDK，它**S3 协议兼容**，能直接连 R2 / OSS / COS / S3。改动量极小。

### 改动 1：[backend/app/core/config.py](backend/app/core/config.py)

新增 3 个可选字段：

```python
# MinIO / S3 兼容存储
MINIO_ENDPOINT: str
MINIO_ACCESS_KEY: str
MINIO_SECRET_KEY: str
MINIO_BUCKET: str
MINIO_SECURE: bool = False        # ← 新增：HTTPS 开关，云厂商一律 True
MINIO_REGION: str | None = None   # ← 新增：R2 必填 "auto"，OSS 可空
MINIO_PUBLIC_BASE_URL: str | None = None  # ← 新增：公开访问域名（avatar 等用）
```

### 改动 2：[backend/app/core/storage.py](backend/app/core/storage.py)

把 `Minio(...)` 构造改成读上面的字段：

```python
_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,            # ← 改这里
    region=settings.MINIO_REGION,            # ← 加这里
)
```

并把 `make_bucket` 那段去掉（云端 bucket 在控制台创建，代码里别动）：

```python
# 删除这两行：
# if not _client.bucket_exists(settings.MINIO_BUCKET):
#     _client.make_bucket(settings.MINIO_BUCKET)
```

### 改动 3：[backend/scripts/init_minio.py](backend/scripts/init_minio.py)

这个脚本不再需要——R2/OSS 的 bucket 和公开策略都在控制台点几下就行。**直接删掉或保留不调用**。

### 改动 4：avatars 公开读

R2 / OSS 的"公开访问"配置方式：

- **R2**：控制台 → bucket → Settings → Public Access → 绑一个自定义域名（如 `cdn.yourdomain.com`），或开 `r2.dev` 临时域名
- **OSS**：控制台 → bucket → 权限管理 → 读写权限改"公共读"（仅 avatars/ 目录可在 bucket policy 里限制）

把公开访问域名填到 `MINIO_PUBLIC_BASE_URL`，在生成 avatar URL 的地方用它替代签名 URL。

> 这一步要不要做取决于你的代码里 avatar 怎么访问。如果一直走 `/qingkong/files/...` 后端转发，可以**不改**，所有访问都走签名 URL，省心。

---

## 四、新的 compose 文件

新建 [docker-compose.minimal.yml](docker-compose.minimal.yml)：去掉 postgres / minio，只留 redis + backend + nginx。

```yaml
name: qingkong-minimal

services:
  redis:
    image: redis:7-alpine
    container_name: qingkong-redis
    restart: always
    command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}", "--appendonly", "yes"]
    volumes:
      - redis_data:/data
    networks: [qingkong-net]
    mem_limit: 100m            # ← 限制内存，防止跑飞
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: qingkong/backend:latest    # ← 不在服务器构建，本地构建后推送
    container_name: qingkong-backend
    restart: always
    environment:
      DATABASE_URL: ${DATABASE_URL}                # ← 直接用 Neon 连接串
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      MINIO_ENDPOINT: ${MINIO_ENDPOINT}
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
      MINIO_BUCKET: ${MINIO_BUCKET}
      MINIO_SECURE: "true"                         # ← 云存储一律 HTTPS
      MINIO_REGION: ${MINIO_REGION:-auto}          # ← R2 用 auto
      SECRET_KEY: ${JWT_SECRET_KEY}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES:-30}
      REFRESH_TOKEN_EXPIRE_DAYS: ${REFRESH_TOKEN_EXPIRE_DAYS:-7}
      DEBUG: "false"
    depends_on:
      redis: { condition: service_healthy }
    networks: [qingkong-net]
    mem_limit: 350m

  nginx:
    image: qingkong/nginx:latest
    container_name: qingkong-nginx
    restart: always
    ports:
      - "${NGINX_HTTP_PORT:-3847}:80"
    depends_on:
      - backend
    networks: [qingkong-net]
    mem_limit: 80m

volumes:
  redis_data:

networks:
  qingkong-net:
    driver: bridge
```

关键点：
- 没有 `build:` 字段，**全部用预构建镜像**（避免在 2G 服务器上构建 OOM）
- 每个服务加 `mem_limit`，防止内存泄漏拖垮系统
- DATABASE_URL 直接用云数据库的连接串

---

## 五、新的 .env.production

```bash
# ── Nginx ──
NGINX_HTTP_PORT=3847

# ── 云数据库（Neon 给的连接串，注意改成 asyncpg 协议） ──
# Neon 给的格式: postgresql://user:pass@xxx.neon.tech/dbname?sslmode=require
# 我们要改成：    postgresql+asyncpg://user:pass@xxx.neon.tech/dbname?ssl=require
DATABASE_URL=postgresql+asyncpg://YOUR_USER:YOUR_PASS@xxx.neon.tech/qingkong?ssl=require

# ── Redis（本机，保留密码） ──
REDIS_PASSWORD=CHANGE_ME_STRONG

# ── 对象存储（Cloudflare R2 示例） ──
MINIO_ENDPOINT=<account_id>.r2.cloudflarestorage.com
MINIO_ACCESS_KEY=<R2_API_TOKEN_ACCESS_KEY>
MINIO_SECRET_KEY=<R2_API_TOKEN_SECRET_KEY>
MINIO_BUCKET=qingkong
MINIO_REGION=auto

# ── JWT ──
JWT_SECRET_KEY=<openssl rand -hex 48 生成>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> ⚠️ Neon 给的连接串协议是 `postgresql://`，但项目用的是 `asyncpg` 异步驱动，需要改成 `postgresql+asyncpg://`，且 `sslmode=require` 要改写成 `ssl=require`。这个坑必踩。

---

## 六、构建策略：本地构建 → 推送镜像

2G 服务器构建 Docker 镜像很容易 OOM。最稳的做法是**在你的开发机构建好，推送到镜像仓库，服务器只 pull**。

### 选择镜像仓库（免费）

| 选项 | 优点 | 缺点 |
|------|------|------|
| Docker Hub | 最通用 | 国内 pull 慢，需要镜像加速 |
| **阿里云容器镜像服务（个人版）** | 国内快，免费 | 要实名 |
| GitHub Container Registry (ghcr.io) | 跟代码仓一起管 | 国内访问偶尔慢 |

推荐：**阿里云个人版 ACR**（免费、快）。

### 构建并推送（开发机执行）

```powershell
# 1) 登录阿里云 ACR（密码在阿里云控制台设置）
docker login --username=<你的用户名> registry.cn-hangzhou.aliyuncs.com

# 2) 构建镜像（项目根目录执行）
docker build -t registry.cn-hangzhou.aliyuncs.com/<你的命名空间>/qingkong-backend:latest -f backend/Dockerfile .
docker build -t registry.cn-hangzhou.aliyuncs.com/<你的命名空间>/qingkong-nginx:latest -f nginx/Dockerfile .

# 3) 推送
docker push registry.cn-hangzhou.aliyuncs.com/<你的命名空间>/qingkong-backend:latest
docker push registry.cn-hangzhou.aliyuncs.com/<你的命名空间>/qingkong-nginx:latest
```

然后把 `docker-compose.minimal.yml` 里的 `image:` 字段改成上面的完整路径即可。

> 后续每次发布只需要 `docker build && docker push` → 服务器 `docker compose pull && docker compose up -d`。零停机更新基本现实。

---

## 七、部署步骤（首次上线）

假设你已经买好了 2G 服务器，以下在服务器上执行：

### 1. 装 Docker（一行脚本）

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2. 配置镜像仓库登录

```bash
docker login registry.cn-hangzhou.aliyuncs.com
```

### 3. 拉取项目（只需要 compose 文件 + .env）

```bash
mkdir -p ~/qingkong && cd ~/qingkong
# 把以下两个文件 scp 上来即可，不需要整个仓库
# - docker-compose.minimal.yml
# - .env.production
```

### 4. 准备 .env.production

按上面第五节的模板填好。先把 Neon、R2 的资源开好（5分钟）：

- **Neon**: 注册 → Create Project → 选地区（推荐 Singapore） → 复制连接串
- **Cloudflare R2**: 注册 → R2 → Create bucket "qingkong" → API Tokens → Create token (Object Read & Write)

### 5. 启动

```bash
docker compose --env-file .env.production -f docker-compose.minimal.yml pull
docker compose --env-file .env.production -f docker-compose.minimal.yml up -d
```

### 6. 数据库迁移（首次必做）

```bash
docker compose --env-file .env.production -f docker-compose.minimal.yml \
  exec backend alembic upgrade head
```

### 7. 检查

```bash
docker compose -f docker-compose.minimal.yml ps     # 服务全 healthy
docker stats --no-stream                            # 看内存占用
curl http://127.0.0.1/qingkong/health               # 应返回 {"status":"ok"}
```

---

## 八、HTTPS（强烈建议）

最简单的方案：在 nginx 容器**前面**加一层 [Caddy](https://caddyserver.com/)，它会自动申请 Let's Encrypt 证书。

`docker-compose.minimal.yml` 加一段：

```yaml
  caddy:
    image: caddy:2-alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
    networks: [qingkong-net]
    mem_limit: 50m
```

把原来的 nginx ports 改成不暴露（删掉 `ports:`），只内网通信。

新建 `Caddyfile`：

```
yourdomain.com {
    reverse_proxy nginx:80
}
```

DNS 把域名 A 记录指到服务器 IP，等几分钟，HTTPS 自动就有了。

---

## 九、成本估算（路径 B / 自用博客流量）

| 项 | 月成本 |
|----|--------|
| 腾讯云轻量香港 2核2G | ¥24（年付 ¥288 摊到月）|
| Neon Postgres 免费档 | ¥0 |
| Cloudflare R2 免费档（< 10GB） | ¥0 |
| 域名 .com | ¥6（年付 ¥72 摊到月）|
| **合计** | **¥30/月** |

超过免费额度后：
- Neon Pro 起步 $19/月（一般用不到）
- R2 超过 10GB 后 $0.015/GB（10GB 以上每月几毛钱级别）

---

## 十、常见问题

**Q: 为什么不直接连 Neon 而要走 asyncpg+ssl=require？**
项目用的 SQLAlchemy 异步驱动是 asyncpg，它对 SSL 参数命名跟同步 psycopg 不一样。`sslmode=require`（psycopg 风格）会被 asyncpg 当成未知参数报错。

**Q: R2 不在中国大陆，国内访问慢吗？**
- 文件上传/下载：走 Cloudflare 的 anycast 网络，国内访问通常 200-400ms，自用够了
- 如果嫌慢，可以绑自定义域名 + 套 Cloudflare CDN，速度会好很多

**Q: 路径 A（全国内）的差异点？**
- DATABASE_URL 改成腾讯云数据库内网地址（前提：服务器和 DB 在同一区域）
- MINIO_ENDPOINT 改成 `oss-cn-hangzhou.aliyuncs.com`（按地域）
- MINIO_REGION 设为 `oss-cn-hangzhou`
- MINIO_SECURE 仍然是 `true`

**Q: 我能不能先用 2G 跑全栈，扛不住再迁移？**
理论上可以，但 MinIO 的数据迁移到 R2/OSS 是个体力活（要写脚本扫库改 key）。建议**第一次就走外置方案**，省一次迁移。

---

## 十一、还需要我做什么？

下面这些动作我可以接着做，告诉我先做哪个：

1. ✏️  改 [backend/app/core/storage.py](backend/app/core/storage.py) 和 [config.py](backend/app/core/config.py)，加 `MINIO_SECURE` / `MINIO_REGION` 支持
2. 📄  生成 [docker-compose.minimal.yml](docker-compose.minimal.yml) 实际文件
3. 🧪  在你本地用 R2 测试存储（写一个最小验证脚本）
4. 🛠  写一份 PowerShell 构建+推送的一键脚本（避免手敲三行 docker build）
