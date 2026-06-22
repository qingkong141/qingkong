<#
  臻橙云盘 - 打包脚本（开发机执行）
  产出 deploy.zip，丢给运维即可
#>

$ErrorActionPreference = "Stop"

Write-Host "=== 臻橙云盘 部署包构建 ===" -ForegroundColor Cyan
Write-Host ""

# 检查 docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 请先安装 Docker Desktop" -ForegroundColor Red
    exit 1
}

# 清理旧产物
$outDir = "$PSScriptRoot\..\deploy-package"
Remove-Item -Recurse -Force $outDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "$outDir\images" | Out-Null

# 构建镜像
Write-Host "[1/4] 构建 Docker 镜像..." -ForegroundColor Yellow
docker compose -f "$PSScriptRoot\..\docker-compose.prod.yml" build --no-cache
if ($LASTEXITCODE -ne 0) { throw "构建失败" }

# 导出镜像
Write-Host "[2/4] 导出镜像..." -ForegroundColor Yellow
docker save -o "$outDir\images\yunpan-backend.tar" yunpan/backend:latest
docker save -o "$outDir\images\yunpan-nginx.tar"   yunpan/nginx:latest

# 复制部署文件
Write-Host "[3/4] 复制部署文件..." -ForegroundColor Yellow
Copy-Item "$PSScriptRoot\..\docker-compose.prod.yml" "$outDir\"
Copy-Item "$PSScriptRoot\..\nginx\nginx.conf" "$outDir\nginx.conf" -ErrorAction SilentlyContinue
Copy-Item "$PSScriptRoot\deploy.sh" "$outDir\"
Copy-Item "$PSScriptRoot\OPS_README.md" "$outDir\README.md"

# 复制 .env 模板（不含真实密码）
if (Test-Path "$PSScriptRoot\..\backend\.env") {
    Copy-Item "$PSScriptRoot\..\backend\.env" "$outDir\.env.template"
} else {
    Write-Host "⚠ 未找到 backend\.env，生成空白模板" -ForegroundColor DarkYellow
    @"
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/yunpan
REDIS_URL=redis://:password@redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=CHANGE_ME
MINIO_BUCKET=yunpan
SECRET_KEY=CHANGE_ME_JWT_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=false
"@ | Out-File -Encoding utf8 "$outDir\.env.template"
}

# 打包
Write-Host "[4/4] 打包 deploy.zip..." -ForegroundColor Yellow
$zipPath = "$PSScriptRoot\..\deploy.zip"
Remove-Item $zipPath -ErrorAction SilentlyContinue
Compress-Archive -Path "$outDir\*" -DestinationPath $zipPath

# 清理临时目录
Remove-Item -Recurse -Force $outDir -ErrorAction SilentlyContinue

$size = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)
Write-Host ""
Write-Host "✅ 完成！部署包: deploy.zip ($size MB)" -ForegroundColor Green
Write-Host ""
Write-Host "发给运维的文件:" -ForegroundColor Cyan
Write-Host "  📦 deploy.zip" -ForegroundColor White
Write-Host ""
Write-Host "运维操作步骤:" -ForegroundColor Cyan
Write-Host "  1. 解压: unzip deploy.zip" -ForegroundColor White
Write-Host "  2. 编辑 .env.template → 改成真实密码, 保存为 .env" -ForegroundColor White
Write-Host "  3. 运行: bash deploy.sh" -ForegroundColor White
