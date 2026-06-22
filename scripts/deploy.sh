#!/usr/bin/env bash
# ═══════════════════════════════════════════════
# 臻橙云盘 - 一键部署脚本（运维在服务器执行）
# 前提：已安装 Docker (≥20.10) 和 docker compose
# 用法：bash deploy.sh
# ═══════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════╗${NC}"
echo -e "${CYAN}║   臻橙云盘  部署脚本             ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════╝${NC}"
echo ""

# ── 检查 Docker ────────────────────────
if ! command -v docker &>/dev/null; then
    echo -e "${RED}❌ 未安装 Docker，请先执行: curl -fsSL https://get.docker.com | sh${NC}"
    exit 1
fi

# 自动检测 compose 命令（新版内置 docker compose 或旧版独立 docker-compose）
if docker compose version &>/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo -e "${YELLOW}⚠ 未检测到 docker compose，尝试自动安装 docker-compose...${NC}"
    if command -v curl &>/dev/null; then
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose 2>/dev/null && \
        sudo chmod +x /usr/local/bin/docker-compose && \
        COMPOSE="docker-compose"
    fi
    if [ -z "${COMPOSE:-}" ]; then
        echo -e "${RED}❌ 自动安装失败，请手动安装 docker-compose 后再试${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ docker-compose 安装成功${NC}"
fi

COMPOSE_OPTS="-p yunpan"

echo -e "${GREEN}✅ Docker 已就绪 (${COMPOSE})${NC}"

# ── 停止旧容器（更新/重部署时自动处理，不会删数据） ──
echo -e "${YELLOW}检查并停止旧服务...${NC}"
docker rm -f yunpan-nginx yunpan-backend yunpan-postgres yunpan-redis yunpan-minio 2>/dev/null && \
    echo -e "${GREEN}✅ 旧服务已停止${NC}" || true

# ── 检查 .env ──────────────────────────
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo -e "${YELLOW}⚠ 未找到 .env，从模板创建（使用随机密码）${NC}"
        cp .env.template .env
        echo -e "${YELLOW}   建议部署完成后修改 .env 中的密码并重启服务${NC}"
    else
        echo -e "${RED}❌ 未找到 .env 或 .env.template 文件${NC}"
        exit 1
    fi
fi

# ── 设置 nginx 配置（如存在 nginx.conf） ──
NGINX_VOL=""
if [ -f "./nginx.conf" ]; then
    mkdir -p nginx
    cp ./nginx.conf ./nginx/nginx.conf
    NGINX_VOL="    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro"
fi

# ── 加载镜像（如果存在 images 目录） ──
if [ -d "images" ] && [ "$(ls -A images 2>/dev/null)" ]; then
    echo -e "${YELLOW}[1/4] 加载 Docker 镜像...${NC}"
    for f in images/*.tar; do
        echo "  加载: $f"
        docker load -q -i "$f"
    done
    echo -e "${GREEN}✅ 镜像加载完成${NC}"
else
    echo -e "${YELLOW}[1/4] 跳过镜像加载（本地构建）${NC}"
fi

# ── 生成附带 nginx 挂载的 compose 文件 ──
echo -e "${YELLOW}[2/4] 准备 compose 配置...${NC}"
cat > docker-compose.run.yml << COMPOSE
services:
  postgres:
    image: postgres:16-alpine
    container_name: yunpan-postgres
    restart: always
    environment:
      POSTGRES_DB: \${POSTGRES_DB}
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks: [yunpan-net]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER} -d \${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: yunpan-redis
    restart: always
    command: ["redis-server", "--requirepass", "\${REDIS_PASSWORD}", "--appendonly", "yes"]
    volumes:
      - redis_data:/data
    networks: [yunpan-net]
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "\${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: yunpan-minio
    restart: always
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: \${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: \${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    networks: [yunpan-net]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: yunpan/backend:latest
    container_name: yunpan-backend
    restart: always
    environment:
      DATABASE_URL: \${DATABASE_URL}
      REDIS_URL: \${REDIS_URL}
      MINIO_ENDPOINT: \${MINIO_ENDPOINT}
      MINIO_ACCESS_KEY: \${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: \${MINIO_SECRET_KEY}
      MINIO_BUCKET: \${MINIO_BUCKET}
      SECRET_KEY: \${SECRET_KEY}
      ACCESS_TOKEN_EXPIRE_MINUTES: "30"
      REFRESH_TOKEN_EXPIRE_DAYS: "7"
      DEBUG: "false"
    depends_on:
      - postgres
      - redis
      - minio
    networks: [yunpan-net]

  nginx:
    image: yunpan/nginx:latest
    container_name: yunpan-nginx
    restart: always
    ports:
      - "3847:80"
    depends_on:
      - backend
    networks: [yunpan-net]
${NGINX_VOL}
volumes:
  postgres_data:
  redis_data:
  minio_data:

networks:
  yunpan-net:
    driver: bridge
COMPOSE

echo -e "${GREEN}✅ 配置就绪${NC}"

# ── 启动 ──────────────────────────────
echo -e "${YELLOW}[3/4] 启动服务...${NC}"
${COMPOSE} ${COMPOSE_OPTS} -f docker-compose.run.yml --env-file .env up -d

echo ""
echo -e "${GREEN}✅ 服务已启动${NC}"
echo ""
${COMPOSE} ${COMPOSE_OPTS} -f docker-compose.run.yml ps

# ── 数据库迁移 ────────────────────────
echo ""
echo -e "${YELLOW}[4/4] 执行数据库迁移...${NC}"
sleep 5  # 等 backend 完全就绪
${COMPOSE} ${COMPOSE_OPTS} -f docker-compose.run.yml exec -T backend alembic upgrade head 2>/dev/null && \
    echo -e "${GREEN}✅ 数据库迁移完成${NC}" || \
    echo -e "${YELLOW}⚠ 迁移可能需要重试，稍后手动执行: ${COMPOSE} ${COMPOSE_OPTS} -f docker-compose.run.yml exec backend alembic upgrade head${NC}"


echo ""
echo -e "${CYAN}╔══════════════════════════════════╗${NC}"
echo -e "${CYAN}║   部署完成！                     ║${NC}"
echo -e "${CYAN}╠══════════════════════════════════╣${NC}"
echo -e "${CYAN}║  管理台:  http://<IP>:3847/admin ${NC}"
echo -e "${CYAN}║  健康检查: curl /yunpan/health ${NC}"
echo -e "${CYAN}║  查看日志: ${COMPOSE} ${COMPOSE_OPTS} -f docker-compose.run.yml logs -f ${NC}"
echo -e "${CYAN}╚══════════════════════════════════╝${NC}"
