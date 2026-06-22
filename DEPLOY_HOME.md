# 青空 QingKong 家用电脑部署方案

> 把家里的电脑变成一台不需要公网 IP、不需要备案的"自有服务器"。
> 数据全在你硬盘上，外部只依赖 Cloudflare Tunnel（免费）。

---

## 一、整体架构

```
                    互联网访问者
                        │
                        ▼
                ┌───── Cloudflare ─────┐
                │  (CDN + DDoS + HTTPS) │
                └───────────┬───────────┘
                            │ 加密隧道
                            ▼
                ┌─── 你家电脑 (内网) ───┐
                │                       │
                │   cloudflared 进程    │ ← 主动连出去打洞
                │         │             │
                │         ▼             │
                │   nginx :80 ──┬─→ backend (FastAPI)  │
                │               ├─→ nuxt-blog (SSR)    │
                │               ↓                       │
                │   postgres / redis / minio (本机)    │
                └───────────────────────────────────────┘
```

**关键特性**：
- ✅ 不需要公网 IP（家里 NAT 后面也能用）
- ✅ 不需要备案（Cloudflare 不在大陆）
- ✅ 自动 HTTPS（Cloudflare 颁发证书）
- ✅ 免费 DDoS 防护
- ✅ 数据完全在你硬盘上
- ⚠️ 家里断电/断网就挂（自用可接受）

---

## 二、准备清单

开工前确认这些都搞定：

### 必备
- [ ] 一台能 7×24 开机的电脑（4GB+ 内存、50GB+ 硬盘空间）
- [ ] 一个域名（推荐去 [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/) 注册 `.com` 约 $10/年；或 阿里云万网 ¥55/年）
- [ ] 一个 Cloudflare 账号（[cloudflare.com](https://dash.cloudflare.com/sign-up) 免费注册）
- [ ] 项目代码（你已经有了）

### 不需要
- ~~公网 IP~~
- ~~备案~~
- ~~买云服务器~~
- ~~花生壳/ngrok 这种内网穿透~~

---

## 三、操作系统选择

> 你家这台机器之后**只跑这个服务**还是**继续日常使用**？

### 路径 A：装 Ubuntu Server（推荐，长期稳定）

适合：这台机器你打算 24h 开着、专门当服务器用。

- 优点：稳定、省内存（无图形界面）、不会被 Windows 自动更新搞挂
- 代价：要学一点 Linux 命令（其实也就 `cd / ls / nano` 这几个）

### 路径 B：保留 Windows + Docker Desktop（懒人路径）

适合：这台机器你还要日常用、不想重装系统。

- 优点：不动现状
- 代价：Docker Desktop 后台吃 1-2GB 内存；Windows 大版本更新会重启；不能随便关机

**这份文档以路径 A 为主**。如果选 B，跳到第六节看差异。

---

## 四、装 Ubuntu Server（路径 A）

### 1. 制作 U 盘启动盘

1. 下载 [Ubuntu Server 24.04 LTS](https://ubuntu.com/download/server)（约 2.5GB ISO）
2. 下载 [Rufus](https://rufus.ie/)（在你 Windows 开发机上）
3. 插一根 8GB+ 的 U 盘，用 Rufus 把 ISO 写进去（约 10 分钟）

### 2. 装系统

> 这一步在你**家里那台要当服务器的电脑**上做。

1. 插 U 盘开机，开机时按 F2/F12/Del（看主板品牌）进 BIOS，把 U 盘设为第一启动项
2. 进入 Ubuntu 安装界面，**全程一路 Continue / Done**，遇到这两步要注意：
   - **网络配置**：选有线网卡，记下分配的内网 IP（如 `192.168.1.100`）
   - **Profile setup**：设置一个用户名 + 密码，用户名建议 `qingkong`
   - **SSH setup**：⭐ **务必勾上 "Install OpenSSH server"**，否则你后面没法远程操作
   - **Featured Server Snaps**：什么都不勾，跳过
3. 安装完成 → 拔 U 盘 → 重启 → 看到登录提示符

### 3. 从你的开发机 SSH 进去

回到你 Windows 开发机，打开 PowerShell：

```powershell
ssh qingkong@192.168.1.100   # 改成你刚才记下的 IP
```

输密码进去后，所有后续命令都在这个 SSH 会话里跑（不用再坐到那台机器前）。

### 4. 给电脑设置静态 IP（重要）

家里路由器默认会给设备**动态 IP**，过几天 IP 就变了，到时候 SSH 都连不上。

最简单的做法：**进路由器后台，把这台电脑的 MAC 地址绑定固定 IP**。

各家路由器不一样：
- 小米：路由器后台 → 常用设置 → 局域网 → 静态 IP 分配
- 华为：高级 → DHCP 静态地址分配
- TP-Link：DHCP 服务器 → 静态地址分配

把这台电脑绑死成 `192.168.1.100`（或你喜欢的）。

---

## 五、装 Docker

```bash
# 一行脚本，5 分钟
curl -fsSL https://get.docker.com | sudo sh

# 把当前用户加入 docker 组（避免每次敲 sudo）
sudo usermod -aG docker $USER

# 让分组立即生效
newgrp docker

# 验证
docker --version
docker compose version
```

---

## 六、上传项目代码

你的代码在 Windows 上的 `D:\lsl\qingkong`。把它弄到家里这台 Ubuntu 上，两种办法：

### 方法 A：从 GitHub clone（推荐，方便后续更新）

如果项目已经推到 GitHub：

```bash
cd ~
git clone https://github.com/<你的用户名>/qingkong.git
cd qingkong
```

### 方法 B：从开发机 scp 上传（项目还没推 Git）

在你 Windows 开发机的 PowerShell 里：

```powershell
# 在项目根目录下打包（排除 node_modules / venv 等）
cd D:\lsl\qingkong
tar --exclude=node_modules --exclude=venv --exclude=.git -czf qingkong.tar.gz .

# 上传到 Ubuntu 机器
scp qingkong.tar.gz qingkong@192.168.1.100:~/
```

回到 Ubuntu 的 SSH 会话：

```bash
mkdir -p ~/qingkong && cd ~/qingkong
tar -xzf ~/qingkong.tar.gz
rm ~/qingkong.tar.gz
```

---

## 七、配置 .env.production

```bash
cd ~/qingkong
cp .env.production.example .env.production

# 生成 4 个强密码（每条命令复制一次输出）
openssl rand -hex 48        # → JWT_SECRET_KEY
openssl rand -base64 24     # → POSTGRES_PASSWORD
openssl rand -base64 24     # → REDIS_PASSWORD
openssl rand -base64 24     # → MINIO_ROOT_PASSWORD

# 编辑文件，把上面 4 个值填进去
nano .env.production
```

`nano` 编辑器操作：
- 上下左右键移动光标
- 输入修改
- `Ctrl+O` → 回车 保存
- `Ctrl+X` 退出

填好后看一眼内容确认无误：

```bash
cat .env.production
```

> ⚠️ `.env.production` 包含密码，**不要提交到 Git**。`.gitignore` 应该已经排除了，但确认一下没坏处。

---

## 八、启动整套服务

```bash
cd ~/qingkong

# 构建 + 启动（首次约 15-20 分钟，主要是 npm install + Python 依赖）
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build

# 查看状态（应该全部 healthy）
docker compose -f docker-compose.prod.yml ps

# 看实时日志（Ctrl+C 退出，不会停容器）
docker compose -f docker-compose.prod.yml logs -f
```

如果某个服务卡在 `starting` 或反复重启，看它的日志：

```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs nginx
```

---

## 九、数据库迁移 + MinIO 初始化

**首次启动后必做**（创建表、创建 bucket）：

```bash
# Alembic 跑迁移建表
docker compose --env-file .env.production -f docker-compose.prod.yml \
  exec backend alembic upgrade head

# 初始化 MinIO bucket 和公开读策略
docker compose --env-file .env.production -f docker-compose.prod.yml \
  exec backend python scripts/init_minio.py
```

### 本地验证（公网还没通）

```bash
curl http://127.0.0.1/qingkong/health
# 应该返回 {"status":"ok"}

curl -I http://127.0.0.1/
# 应该返回 200，HTML 来自 Nuxt
```

到这一步，**服务在你内网可访问了**（手机连同一 WiFi 浏览器输 `http://192.168.1.100` 也能看到）。下一步把它发布到公网。

---

## 十、Cloudflare Tunnel 配置（核心）

这一步把家里的服务"打洞"到公网。

### 1. 把域名托管到 Cloudflare

> 如果你的域名是在 Cloudflare 买的，这步跳过。

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 点 "Add a Site" → 输入你的域名 → 选 Free 套餐
3. Cloudflare 会列出 2 条 nameserver（如 `xxx.ns.cloudflare.com`）
4. 去你买域名的地方（阿里云/Namecheap 等）的"DNS 服务器"设置，把 nameserver 改成 Cloudflare 给的两条
5. 等 5-30 分钟，Cloudflare 会显示 "Active"

### 2. 创建 Tunnel

1. Cloudflare Dashboard → 左侧 **Zero Trust** → **Networks** → **Tunnels**
2. **Create a tunnel** → Connector 选 **Cloudflared** → Next
3. 起个名字 `qingkong-home` → Save
4. 选 **Linux** → **Debian** → 64-bit → 它会给你一条安装命令，类似：

   ```bash
   curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && \
   sudo dpkg -i cloudflared.deb && \
   sudo cloudflared service install eyJhIjoi...（一长串 token）
   ```

5. **复制这条命令，粘贴到你的 Ubuntu SSH 终端跑**
6. 跑完回到 Cloudflare 页面，会看到 Connector 显示 `HEALTHY` ✅
7. 点 Next 进入 **Public Hostname** 配置：

   | 字段 | 填什么 |
   |------|--------|
   | Subdomain | （空）或 `www` |
   | Domain | 选你的域名 |
   | Path | （空）|
   | Type | `HTTP` |
   | URL | `localhost:80` ← ⭐ 关键，指向你本机 nginx |

8. **Save tunnel**

### 3. 测试公网访问

打开浏览器访问 `https://yourdomain.com`：
- 应该看到你的 Nuxt 博客首页
- 地址栏有 🔒（HTTPS 自动生效）
- F12 → Network → 看请求经过 `cf-ray` header

如果出现 502 / 1033 错误：
- 检查 `docker compose ps` 全部容器是不是 healthy
- 检查 Cloudflare Tunnel 的 Connector 是 healthy

---

## 十一、日常运维命令

放进 `~/qingkong/cheatsheet.md` 留着随时查。

### 看运行状态

```bash
cd ~/qingkong
docker compose -f docker-compose.prod.yml ps
docker stats --no-stream    # 看每个容器的内存/CPU 占用
```

### 看日志

```bash
docker compose -f docker-compose.prod.yml logs -f --tail=100 backend
docker compose -f docker-compose.prod.yml logs -f --tail=100 nginx
```

### 重启某个服务

```bash
docker compose -f docker-compose.prod.yml restart backend
```

### 更新代码后重新发布

```bash
cd ~/qingkong
git pull                    # 或 scp 上传新代码
docker compose --env-file .env.production -f docker-compose.prod.yml \
  up -d --build
```

### 备份数据库

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml \
  exec postgres pg_dump -U qingkong qingkong > ~/backup-$(date +%F).sql
```

建议加一条 cron，每天凌晨 3 点自动备份：

```bash
crontab -e
# 在最后加这一行：
0 3 * * * cd /home/qingkong/qingkong && docker compose --env-file .env.production -f docker-compose.prod.yml exec -T postgres pg_dump -U qingkong qingkong > /home/qingkong/backup-$(date +\%F).sql
```

### 备份 MinIO 文件

```bash
# MinIO 的数据卷
docker run --rm \
  -v qingkong-prod_minio_data:/data \
  -v ~/backups:/backup \
  alpine tar czf /backup/minio-$(date +%F).tar.gz -C /data .
```

---

## 十二、保留 Windows + Docker Desktop 路径（路径 B）

如果你不想装 Ubuntu，直接在现在的 Windows 上跑：

### 1. 装 Docker Desktop

下载：[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

装完后启动，等待右下角 Docker 鲸鱼图标变绿（不再是黄色"starting"）。

### 2. 启动服务

直接在 Windows PowerShell 里跑（路径用 `D:\lsl\qingkong`）：

```powershell
cd D:\lsl\qingkong
copy .env.production.example .env.production
notepad .env.production    # 改密码

docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.production -f docker-compose.prod.yml exec backend alembic upgrade head
docker compose --env-file .env.production -f docker-compose.prod.yml exec backend python scripts/init_minio.py
```

### 3. Cloudflare Tunnel for Windows

下载 Windows 版 cloudflared：
[https://github.com/cloudflare/cloudflared/releases](https://github.com/cloudflare/cloudflared/releases) → 选 `cloudflared-windows-amd64.exe`

把它放到 `C:\cloudflared\cloudflared.exe`，按 Cloudflare 网页给的命令安装服务（命令格式略有不同，参考网页指引）。

### 4. Windows 路径要注意的坑

- **关闭"快速启动"**：控制面板 → 电源选项 → 选择电源按钮的功能 → 启用快速启动取消勾选（否则关机重开后 Docker 启动慢、Tunnel 容易短暂断流）
- **关闭自动更新重启**：组策略 → Windows 更新 → 禁用自动重启
- **休眠会让服务挂**：电源选项 → 一律设为"从不"

老实讲，如果这台机器要长期当服务器用，**装 Ubuntu Server 真的更省心**。

---

## 十三、常见问题

**Q: Cloudflare Tunnel 免费版有限制吗？**
官方文档没明说速率上限。社区实测自用流量（< 100GB/月）完全无感。商用大流量建议升级 Pro。

**Q: 国内访问速度怎么样？**
Cloudflare 在中国大陆没自己节点，国内访客会被路由到香港/日本/美西，延迟 100-300ms。**自用够用**，对 SEO/商业项目不友好。

**Q: 我需要 nginx 容器吗？Tunnel 直接指 backend 不行吗？**
nginx 还是要的——它负责把 `/`、`/admin`、`/blog-admin/`、`/qingkong/*` 等不同路径分发到不同后端容器。Tunnel 只是把外网流量送到 nginx 入口。

**Q: 家里电脑断电了怎么办？**
- 加个 UPS（200-500 元）支持几分钟到半小时
- 来电后服务自动恢复（`docker compose` 已配置 `restart: always`）
- 路由器和光猫也接 UPS，否则没网

**Q: 可以 SSH 远程访问家里电脑吗（出门时维护）？**
能。在 Cloudflare Tunnel 里**多加一条 Public Hostname**：
- Subdomain: `ssh`
- Type: `SSH`
- URL: `localhost:22`

然后用 `cloudflared access ssh --hostname ssh.yourdomain.com` 在外面连。

**Q: 数据备份要存哪里？**
本地 `~/backups/` 是第一份，但**家里硬盘坏了就全没**。建议：
- 加一块 USB 移动硬盘做第二份
- 重要数据再 rclone 同步到 OneDrive / Google Drive

---

## 十四、上线前检查清单

参考 [DEPLOY.md](DEPLOY.md) 第 116 行起的"全链路冒烟测试"，每条都过一遍才算真上线。

特别注意：
- [ ] 浏览器访问 `https://yourdomain.com` 出现 🔒 锁
- [ ] `https://yourdomain.com/admin` 能进后台
- [ ] 手机 4G 网络（非 WiFi）也能访问
- [ ] 家里电脑重启一次，服务自动起来
- [ ] 备份脚本跑一次，能成功生成 `.sql` 文件

---

## 十五、出问题先看哪里？

按这个顺序排查：

```
访问不通 → 1. cloudflared 日志：journalctl -u cloudflared -f
         → 2. Cloudflare Dashboard 看 Tunnel 是否 HEALTHY
         → 3. docker compose ps 看容器是否 healthy
         → 4. 浏览器 F12 看具体错误码（502/1033/520...）

数据没保存 → 1. backend 日志看是否报数据库连接错误
            → 2. docker volume ls 看 postgres_data 还在不在

页面 404   → 1. nginx 日志看请求路径
            → 2. 各前端 vite.config.ts 的 base 是否对得上
```

---

写到这。下一步建议：

1. 先按第三节决定路径 A 还是 B
2. 准备好域名和 Cloudflare 账号
3. 跟着步骤走，每一步遇到问题问我，我一对一帮你查
