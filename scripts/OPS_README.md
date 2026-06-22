# 臻橙云盘 — 运维部署说明

## 你拿到的是一个 zip 包，里面包含：

```
├── deploy.sh              ← 一键部署脚本
├── docker-compose.run.yml ← 自动生成，不用管
├── .env.template          ← 环境变量模板，改成真实密码后保存为 .env
├── nginx.conf             ← Nginx 配置（可选）
└── images/                ← Docker 镜像（后端 + nginx）
```

## 前置条件

- Docker ≥ 20.10（已安装）
- 硬盘 ≥ 20GB 可用空间
- 内存 ≥ 2GB

## 操作步骤（3 步）

```bash
# 1. 解压
unzip deploy.zip -d yunpan && cd yunpan

# 2. 配置密码（每个 CHANGE_ME 都要改）
cp .env.template .env
vim .env

# 3. 执行
bash deploy.sh
```

## 服务端口

| 端口 | 用途 |
|------|------|
| 3847 | 管理台 + API（对外） |

防火墙放行 3847 即可。

## 日常操作

```bash
# 查看状态
docker compose -f docker-compose.run.yml ps

# 查看日志
docker compose -f docker-compose.run.yml logs -f nginx
docker compose -f docker-compose.run.yml logs -f backend

# 重启
docker compose -f docker-compose.run.yml restart backend

# 备份数据库
docker compose -f docker-compose.run.yml exec -T postgres \
  pg_dump -U yunpan yunpan > backup-$(date +%F).sql
```

## 出问题了？

1. `docker compose -f docker-compose.run.yml ps` 看服务状态
2. 有 `unhealthy` 就看该容器日志：`docker logs <容器名>`
3. 搞不定把上面两条输出发给开发
