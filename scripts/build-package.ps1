<#
  Build deploy.zip for yunpan
  Usage: powershell -ExecutionPolicy Bypass -File .\scripts\build-package.ps1
#>
$ErrorActionPreference = "Continue"

Write-Host "=== yunpan deploy package builder ===" -ForegroundColor Cyan

$root = Split-Path -Parent $PSScriptRoot
$outDir = "$root\deploy-package"

# Clean
Remove-Item -Recurse -Force $outDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "$outDir\images" | Out-Null

# Build images
Write-Host "[1/4] Building Docker images..." -ForegroundColor Yellow
Push-Location $root
docker compose -f docker-compose.prod.yml build --no-cache
if ($LASTEXITCODE -ne 0) { throw "Build failed" }
Pop-Location

# Pull infrastructure images (in case they're not cached)
Write-Host "[2/5] Pulling infrastructure images..." -ForegroundColor Yellow
docker pull postgres:16-alpine
docker pull redis:7-alpine
docker pull minio/minio:latest

# Export images
Write-Host "[3/5] Exporting images..." -ForegroundColor Yellow
docker save -o "$outDir\images\yunpan-backend.tar" yunpan/backend:latest
docker save -o "$outDir\images\yunpan-nginx.tar"   yunpan/nginx:latest
docker save -o "$outDir\images\postgres.tar"        postgres:16-alpine
docker save -o "$outDir\images\redis.tar"            redis:7-alpine
docker save -o "$outDir\images\minio.tar"            minio/minio:latest

# Copy deploy files
Write-Host "[4/5] Copying deploy files..." -ForegroundColor Yellow
Copy-Item "$root\docker-compose.prod.yml" "$outDir\"
Copy-Item "$root\nginx\nginx.conf" "$outDir\nginx.conf" -ErrorAction SilentlyContinue
Copy-Item "$root\scripts\deploy.sh" "$outDir\"
Copy-Item "$root\scripts\OPS_README.md" "$outDir\README.md" -ErrorAction SilentlyContinue

# Create env template
$envTemplate = @'
DATABASE_URL=postgresql+asyncpg://yunpan:YunPan2026Pg@postgres:5432/yunpan
REDIS_URL=redis://:YunPan2026Redis@redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=YunPan2026Minio
MINIO_BUCKET=yunpan
SECRET_KEY=yunpan-jwt-secret-2026
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=false
POSTGRES_DB=yunpan
POSTGRES_USER=yunpan
POSTGRES_PASSWORD=YunPan2026Pg
REDIS_PASSWORD=YunPan2026Redis
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=YunPan2026Minio
'@
$envTemplate | Out-File -Encoding utf8 "$outDir\.env.template"

# Package
Write-Host "[5/5] Creating deploy.zip..." -ForegroundColor Yellow
$zipPath = "$root\deploy.zip"
Remove-Item $zipPath -ErrorAction SilentlyContinue
Compress-Archive -Path "$outDir\*" -DestinationPath $zipPath

# Cleanup
Remove-Item -Recurse -Force $outDir -ErrorAction SilentlyContinue

$size = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)
Write-Host ""
Write-Host "Done: deploy.zip ($size MB)" -ForegroundColor Green
Write-Host "Send deploy.zip to ops, then:"
Write-Host "  1. unzip deploy.zip"
Write-Host "  2. edit .env.template -> save as .env"
Write-Host "  3. bash deploy.sh"
