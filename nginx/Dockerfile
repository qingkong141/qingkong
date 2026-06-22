# ── 阶段 1：构建静态子应用 ──────────────────────
FROM node:24-alpine AS builder

RUN corepack enable && corepack prepare pnpm@10.21.0 --activate

WORKDIR /workspace

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml turbo.json ./
COPY apps/admin-shell/package.json apps/admin-shell/package.json
COPY apps/drive/package.json       apps/drive/package.json
COPY packages packages

RUN pnpm install --filter @yunpan/admin-shell... --filter @yunpan/drive...

COPY apps/admin-shell apps/admin-shell
COPY apps/drive       apps/drive

ENV NODE_ENV=production
RUN pnpm --filter @yunpan/admin-shell build && pnpm --filter @yunpan/drive build

# ── 阶段 2：nginx + 静态资源 ────────────────────
FROM nginx:1.27-alpine AS runtime

RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /workspace/apps/admin-shell/dist /usr/share/nginx/html/admin
COPY --from=builder /workspace/apps/drive/dist       /usr/share/nginx/html/drive

COPY nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]
