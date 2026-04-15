# 晴空 QingKong — 博客 + 云盘系统开发计划

> 利用空闲时间完成，每个「Session」代表一次有效开发时间（约 2~3 小时）
> 工作日晚上 1 Session，周末 2 Session，总计约 **50 Sessions / 3~4 个月**

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| Monorepo | pnpm workspaces + Turborepo | 统一管理所有子项目 |
| 博客前台 | Nuxt 3 | SSR，SEO 友好 |
| 后台主壳 | Vue 3 + qiankun | 微前端基座，可扩展 |
| 博客管理子应用 | Vue 3 + Vite | qiankun 子应用 |
| 云盘子应用 | Vue 3 + Vite | qiankun 子应用 |
| 后端框架 | FastAPI | Python，异步高性能 |
| 数据库 | PostgreSQL | 主数据库 |
| 缓存 | Redis | Token 管理 / 计数 |
| 文件存储 | MinIO | 自托管 S3 兼容存储 |
| 数据库迁移 | Alembic | FastAPI 配套 |
| 认证 | JWT (access + refresh token) | 双 Token 机制 |

---

## 系统架构

```
用户请求
    │
    ▼
  Nginx (统一入口)
    ├── /              → Nuxt 3 博客前台 (SSR)     :3000
    ├── /admin         → Vue 3 + qiankun 主壳      :8080
    │     ├── /admin/blog   → 博客管理子应用        :8081
    │     ├── /admin/drive  → 云盘子应用            :8082
    │     └── /admin/xxx    → 未来扩展子应用        :808x
    └── /api           → FastAPI                   :8000
```

---

## Monorepo 项目结构

```
qingkong/
├── apps/
│   ├── nuxt3-blog/          # 博客前台 (Nuxt 3 SSR)
│   ├── admin-shell/         # 后台主壳 (Vue 3 + qiankun)
│   ├── blog-admin/          # 博客管理子应用 (Vue 3)
│   └── drive/               # 云盘子应用 (Vue 3)
├── packages/
│   ├── shared-types/        # TypeScript 类型定义
│   ├── shared-api/          # API 请求封装
│   ├── shared-ui/           # 公共组件库
│   ├── shared-utils/        # 工具函数
│   └── shared-styles/       # 公共样式变量
├── backend/                 # FastAPI 后端
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── package.json
├── pnpm-workspace.yaml
└── turbo.json
```

---

## 数据库设计

```
users          用户表
  id, username, email, password_hash, avatar, bio
  storage_used, storage_quota, created_at, updated_at

posts          文章表
  id, title, slug(唯一), content(markdown), summary
  cover_image, author_id, status(draft/published/archived)
  view_count, like_count, created_at, updated_at, published_at

categories     分类表
  id, name, slug, description, parent_id(多级分类)

tags           标签表
  id, name, slug, color

post_tags      文章-标签 多对多
  post_id, tag_id

comments       评论表
  id, post_id, author_id, parent_id(嵌套), content
  status(pending/approved), created_at

files          云盘文件表
  id, name, path, parent_id(文件夹), size, mime_type
  storage_key(MinIO key), md5, owner_id
  is_dir, is_deleted, created_at, updated_at

shares         分享表
  id, file_id, owner_id, token(短码)
  password, expire_at, download_count
```

---

## Markdown 处理方案

```
写作流程：
  Vditor 编辑器 → 输入 Markdown → POST API → 存入 PostgreSQL content 字段

展示流程：
  GET API → 取出 raw markdown → markdown-it 渲染 HTML
           + highlight.js  代码高亮
           + katex         数学公式

内嵌图片：
  编辑器粘贴图片 → 调用 POST /upload/image → 存 MinIO
  → 返回访问 URL → 自动插入 ![alt](url) 到编辑器
```

---

## 文件分片上传流程

```
前端                    后端                MinIO
  │                      │                    │
  ├─ 计算 MD5 ──────────▶│                    │
  │◀─ 秒传/uploadId ──────┤                    │
  ├─ 分片1 ─────────────▶├──── 存分片 ────────▶│
  ├─ 分片2 ─────────────▶├──── 存分片 ────────▶│
  ├─ 合并请求 ───────────▶├─── CompleteMultipart▶│
  │◀─ 文件信息 ───────────┤                    │
```

---

## 开发计划（按 Session）

> ✅ 完成  🔄 进行中  ⬜ 未开始

---

### Phase 1 — Monorepo + 基础设施（Sessions 1~5）

- [x] **Session 1**：Monorepo 骨架搭建
  - pnpm workspaces + Turborepo 配置
  - 建好 `apps/` `packages/` 目录结构
  - 根 `package.json` `pnpm-workspace.yaml` `turbo.json` 配置完成
  - **验收**：`pnpm install` 跑通，`turbo run dev` 不报错

- [x] **Session 2**：docker-compose 基础设施
  - PostgreSQL + Redis + MinIO 三个服务配置
  - 数据卷、网络、健康检查配置
  - MinIO 控制台可访问（:9001）
  - **验收**：`docker compose up` 三个服务全绿

- [x] **Session 3**：FastAPI 项目初始化
  - 目录结构（api / models / schemas / services / core）
  - SQLAlchemy async 配置
  - pydantic-settings 环境变量管理
  - **验收**：`GET /health` 接口返回 200

- [ ] **Session 4**：数据库模型设计
  - SQLAlchemy 定义所有表模型
  - `users` `posts` `categories` `tags` `post_tags` `comments` `files` `shares`
  - **验收**：模型文件完成，关系映射正确

- [ ] **Session 5**：Alembic 迁移 + MinIO 初始化
  - Alembic 配置并执行初始迁移
  - MinIO bucket 初始化脚本
  - **验收**：数据库所有表创建成功，bucket 可访问

---

### Phase 2 — 认证系统 + 共享包（Sessions 6~10）

- [ ] **Session 6**：JWT 认证核心
  - 注册/登录接口
  - bcrypt 密码加密
  - access_token + refresh_token 双 token 生成
  - **验收**：Postman 测试注册登录成功，返回两个 token

- [ ] **Session 7**：认证完整闭环
  - refresh_token 存 Redis + 过期管理
  - Token 刷新接口 + 注销接口
  - `get_current_user` 依赖注入
  - **验收**：token 刷新、注销流程完整

- [ ] **Session 8**：用户接口
  - `GET /auth/me` 当前用户信息
  - 修改密码接口
  - 头像上传（存 MinIO）接口
  - **验收**：用户信息模块接口全部通过

- [ ] **Session 9**：shared-types 包
  - 定义 `User` `Post` `FileItem` `Comment` `Share` `Category` `Tag` 类型
  - 发布为 workspace 包
  - **验收**：各 app 可引用 `@qingkong/shared-types`

> 包名前缀统一使用 `@qingkong/`，如：`@qingkong/shared-types` `@qingkong/shared-api` `@qingkong/shared-ui`

- [ ] **Session 10**：shared-api 包
  - axios 实例（请求拦截自动带 Token，响应拦截统一错误处理）
  - 封装认证相关 API 函数
  - **验收**：shared-api 可在 app 中调用登录接口

---

### Phase 3 — 后台主壳（Sessions 11~13）

- [ ] **Session 11**：admin-shell 初始化
  - Vue 3 + Vite 项目创建
  - qiankun 安装配置
  - 子应用注册表结构设计
  - **验收**：主壳项目启动，qiankun 初始化不报错

- [ ] **Session 12**：登录页 + 路由守卫
  - 登录页 UI + 调用 shared-api
  - Token 本地存储管理
  - 路由守卫（未登录跳登录页）
  - **验收**：登录跳转逻辑完整

- [ ] **Session 13**：主壳布局
  - 顶栏（用户头像 / 退出登录）
  - 侧边栏（动态菜单，子应用注册即出现）
  - 子应用挂载容器 `#micro-container`
  - **验收**：后台整体框架可展示

---

### Phase 4 — 博客后端 API（Sessions 14~18）

- [ ] **Session 14**：文章 CRUD
  - 创建/更新（slug 自动生成）/删除/查单篇
  - 状态机（draft → published → archived）
  - **验收**：文章增删改查接口通过

- [ ] **Session 15**：文章列表查询
  - 分页
  - 按分类/标签/状态筛选
  - PostgreSQL 全文搜索（FTS）
  - **验收**：列表接口支持筛选和搜索

- [ ] **Session 16**：分类 + 标签 CRUD
  - 分类支持父子多级结构
  - 标签 CRUD
  - 文章关联分类/标签接口
  - **验收**：分类标签接口完成

- [ ] **Session 17**：评论系统 + 统计
  - 嵌套评论（发表/审核/删除）
  - 文章浏览量（Redis incr）
  - 点赞接口
  - **验收**：评论模块接口通过

- [ ] **Session 18**：图片上传
  - 接收图片 → 压缩处理 → 存 MinIO → 返回访问 URL
  - 文章封面上传同理
  - **验收**：图片上传返回可访问的 URL

---

### Phase 5 — 博客管理子应用（Sessions 19~25）

- [ ] **Session 19**：blog-admin 接入 qiankun
  - Vue 3 + Vite 初始化
  - 配置 qiankun 生命周期（bootstrap / mount / unmount）
  - 接入主壳，路由前缀配置
  - **验收**：主壳能加载博客管理子应用

- [ ] **Session 20**：文章列表页
  - 表格展示（标题/状态/发布时间）
  - 分页 + 状态筛选
  - 批量删除
  - **验收**：文章列表页完成

- [ ] **Session 21**：Vditor 编辑器集成
  - 安装配置 Vditor
  - 工具栏配置（标题/列表/代码块/图片）
  - 图片上传对接（调 shared-api）
  - 实时预览
  - **验收**：编辑器可正常输入和预览 Markdown

- [ ] **Session 22**：文章编辑页
  - 封面图上传
  - 关联分类/标签选择器
  - 草稿自动保存（定时 30s）
  - 发布/存草稿/预览按钮
  - **验收**：完整写文章流程跑通

- [ ] **Session 23**：分类 + 标签管理页
  - 分类树形表格（支持多级）
  - 标签列表（带颜色选择）
  - **验收**：分类标签管理页完成

- [ ] **Session 24**：评论管理页
  - 评论列表（带文章名/评论者/内容）
  - 审核通过/拒绝/删除操作
  - **验收**：评论审核流程完成

- [ ] **Session 25**：shared-ui 补充 + 联调
  - 补充公共组件（分页/确认弹窗/上传组件）
  - blog-admin 整体联调
  - **验收**：博客后台完整可用

---

### Phase 6 — Nuxt 3 博客前台（Sessions 26~34）

- [ ] **Session 26**：Nuxt 3 初始化
  - 项目创建，配置 SSR/SSG 混合渲染规则
  - 集成 shared-api、shared-types
  - 全局样式、字体配置
  - **验收**：Nuxt 3 启动，能调通 API

- [ ] **Session 27**：首页文章列表（SSG）
  - PostCard 组件
  - 分页
  - 标签云侧边栏
  - **验收**：首页展示文章列表

- [ ] **Session 28**：文章详情页（SSR）
  - `markdown-it` 渲染
  - `highlight.js` 代码块高亮
  - `katex` 数学公式支持
  - **验收**：文章内容正确渲染

- [ ] **Session 29**：TOC 目录 + 阅读进度
  - 自动提取标题生成目录
  - 锚点跳转
  - 滚动时高亮当前章节
  - 顶部阅读进度条
  - **验收**：TOC 交互流畅

- [ ] **Session 30**：评论区 + 点赞
  - 嵌套评论展示
  - 发表评论（需登录）
  - 点赞按钮动效
  - **验收**：评论互动功能完成

- [ ] **Session 31**：标签页 + 分类页
  - `/tags/:tag` 标签筛选文章
  - `/categories/:cat` 分类筛选文章
  - **验收**：筛选页完成

- [ ] **Session 32**：搜索页
  - 搜索框（防抖）
  - 调用 FTS 接口
  - 关键词高亮
  - **验收**：搜索功能可用

- [ ] **Session 33**：SEO 完善
  - 每篇文章动态 `<meta>` 标签
  - Open Graph（微信/Twitter 分享卡片）
  - `sitemap.xml` 自动生成
  - `robots.txt`
  - **验收**：分享链接有预览卡片

- [ ] **Session 34**：响应式 + 联调
  - 移动端适配
  - Nuxt 3 整体联调
  - **验收**：手机端展示正常，前台完整可用

---

### Phase 7 — 云盘后端 API（Sessions 35~40）

- [ ] **Session 35**：文件树查询 + 文件夹 CRUD
  - 按 `parent_id` 查询目录内容
  - 创建/重命名/删除文件夹
  - **验收**：目录结构接口完成

- [ ] **Session 36**：文件普通上传
  - 接收文件 → 计算 MD5
  - 秒传判断（MD5 已存在直接返回）
  - 存 MinIO → 写 DB
  - **验收**：上传文件并秒传功能完成

- [ ] **Session 37**：分片上传
  - 初始化分片任务
  - 上传各分片
  - 合并（MinIO CompleteMultipartUpload）
  - **验收**：大文件分片上传完成

- [ ] **Session 38**：文件下载 + 移动
  - 下载：MinIO 预签名 URL（有效期 10 分钟）
  - 重命名接口
  - 移动（修改 `parent_id`）
  - **验收**：下载/重命名/移动接口完成

- [ ] **Session 39**：分享链接
  - 生成短码 token
  - 可选密码保护
  - 过期时间设置
  - 公开访问接口（验证密码/过期）
  - 下载计数统计
  - **验收**：分享链接完整流程通过

- [ ] **Session 40**：回收站 + 配额
  - 软删除（`is_deleted=true`）
  - 还原文件
  - 彻底删除（同步删 MinIO）
  - 用户存储配额统计
  - **验收**：回收站和配额接口完成

---

### Phase 8 — 云盘前端（Sessions 41~47）

- [ ] **Session 41**：drive 接入 qiankun + 布局
  - Vue 3 + Vite 初始化
  - 接入 qiankun 主壳
  - 文件管理器整体布局（左侧目录树 + 右侧内容区 + 面包屑）
  - **验收**：子应用挂载，布局展示正常

- [ ] **Session 42**：文件列表/网格展示
  - 列表视图（表格：名称/大小/修改时间）
  - 网格视图（缩略图卡片）
  - 视图切换
  - 面包屑路径导航
  - **验收**：文件展示和导航完成

- [ ] **Session 43**：拖拽上传 + 进度条
  - 拖拽上传区域
  - 分片上传对接
  - 实时进度条显示
  - 秒传提示
  - **验收**：文件上传功能完整

- [ ] **Session 44**：右键菜单
  - 右键弹出菜单
  - 下载（打开预签名 URL）
  - 重命名（行内编辑）
  - 移动（弹窗选目录）
  - 删除（移入回收站）
  - 创建分享链接
  - **验收**：右键操作全部完成

- [ ] **Session 45**：文件预览
  - 图片预览（lightbox 放大）
  - 视频在线播放
  - PDF 预览
  - 纯文本/代码文件预览
  - **验收**：主要文件类型可预览

- [ ] **Session 46**：分享管理 + 分享访问页
  - 我的分享列表（含状态/访问次数）
  - 设置密码/修改过期时间
  - 公开分享访问页（输密码/下载）
  - **验收**：分享完整流程通过

- [ ] **Session 47**：回收站 + 配额展示
  - 回收站文件列表
  - 还原/彻底删除操作
  - 顶部存储配额进度条
  - **验收**：云盘功能完整

---

### Phase 9 — 部署与上线（Sessions 48~50）

- [ ] **Session 48**：Nginx 配置
  - 统一路由分发规则
  - `/` → Nuxt 3，`/admin` → qiankun，`/api` → FastAPI
  - gzip 压缩、静态资源缓存配置
  - **验收**：所有路径通过 Nginx 正确转发

- [ ] **Session 49**：Docker 生产环境
  - 各服务 Dockerfile（多阶段构建）
  - 生产环境变量管理（`.env.production`）
  - docker-compose.prod.yml
  - **验收**：生产镜像构建成功

- [ ] **Session 50**：全链路联调 + 上线
  - 完整流程测试（注册→登录→写博客→上传文件→分享）
  - Bug 修复
  - 正式上线
  - **验收**：系统完整可用

---

## 里程碑

| 里程碑 | Session | 内容 |
|--------|---------|------|
| M1 | Session 10 | 认证系统 + 共享包完成，后台可登录 |
| M2 | Session 18 | 博客后端 API 全部完成 |
| M3 | Session 25 | 博客后台（含编辑器）可用 |
| M4 | Session 34 | Nuxt 3 博客前台上线，SEO 完整 |
| M5 | Session 40 | 云盘后端 API 全部完成 |
| M6 | Session 47 | 云盘前端完整可用 |
| M7 | Session 50 | 整体上线 |

---

## 空闲时间节奏参考

```
工作日晚上  1 Session / 天  (~2h)
周末        2 Session / 天  (~4h)

每周约 9 Sessions
50 Sessions ≈ 6 周（全力）~ 4 个月（兼顾生活）
```

---

## 待决策事项

- [ ] 服务器选型（云服务器 / 本地 NAS 自托管）
- [ ] 域名准备
- [ ] 是否需要 HTTPS（Let's Encrypt 免费证书）
- [ ] 博客是否对外公开 or 仅自用
- [ ] 云盘存储容量规划

---

*计划生成日期：2026-04-14*
*项目名称：晴空 QingKong*
*Git 仓库：qingkong*
