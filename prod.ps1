# ══════════════════════════════════════════════════════════
#  生产环境 docker compose 包装脚本（Windows PowerShell）
#  目的：强制使用 .env.production + docker-compose.prod.yml，
#        避免手滑忘记 --env-file 导致 JWT_SECRET_KEY / MINIO_BUCKET 变空
#
#  用法：
#    .\prod.ps1 up           # 启动
#    .\prod.ps1 up -d        # 后台启动（默认就是 -d，见下）
#    .\prod.ps1 down         # 停止并删除容器
#    .\prod.ps1 ps           # 查看容器状态
#    .\prod.ps1 logs backend # 查看 backend 日志
#    .\prod.ps1 logs -f nginx
#    .\prod.ps1 build backend
#    .\prod.ps1 exec backend alembic upgrade head
#    .\prod.ps1 exec backend python scripts/init_minio.py
# ══════════════════════════════════════════════════════════

$ErrorActionPreference = 'Stop'

$EnvFile  = '.env.production'
$Compose  = 'docker-compose.prod.yml'

if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ 缺少 $EnvFile，请先复制模板：" -ForegroundColor Red
    Write-Host "   Copy-Item .env.production.example $EnvFile"
    exit 1
}
if (-not (Test-Path $Compose)) {
    Write-Host "❌ 缺少 $Compose" -ForegroundColor Red
    exit 1
}

# 子命令默认美化：up 自动加 -d（除非用户自己指定了别的）
$cmd = $args
if ($cmd.Count -ge 1 -and $cmd[0] -eq 'up' -and -not ($cmd -contains '-d')) {
    $cmd += '-d'
}

& docker compose --env-file $EnvFile -f $Compose @cmd
