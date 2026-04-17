# syntax=docker/dockerfile:1.6
# 构建上下文：仓库根目录（docker-compose.prod.yml 设置 context: .）

# ── 阶段 1：依赖 + 构建 ──────────────────────────
FROM node:24-alpine AS builder

RUN corepack enable && corepack prepare pnpm@10.21.0 --activate

WORKDIR /workspace

# 先拷 lockfile 与 workspace 声明以最大化缓存命中
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml turbo.json ./
COPY apps/nuxt3-blog/package.json             apps/nuxt3-blog/package.json
COPY packages packages

# Nuxt blog 用到的 workspace 包：shared-types（其它不强依赖）
RUN pnpm install --filter @qingkong/nuxt3-blog... --frozen-lockfile

# 拷业务源码
COPY apps/nuxt3-blog apps/nuxt3-blog

RUN pnpm --filter @qingkong/nuxt3-blog build

# ── 阶段 2：运行时（Node 直接跑 .output/server） ──
FROM node:24-alpine AS runtime

ENV NODE_ENV=production \
    NITRO_PORT=3000 \
    NITRO_HOST=0.0.0.0

WORKDIR /app

COPY --from=builder /workspace/apps/nuxt3-blog/.output ./.output

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000/ >/dev/null 2>&1 || exit 1

CMD ["node", ".output/server/index.mjs"]
