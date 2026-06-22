<#
  Build deploy.zip for yunpan
  Usage: powershell -ExecutionPolicy Bypass -File .\scripts\build-package.ps1
#>
$ErrorActionPreference = "Stop"

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

# Export images
Write-Host "[2/4] Exporting images..." -ForegroundColor Yellow
docker save -o "$outDir\images\yunpan-backend.tar" yunpan/backend:latest
docker save -o "$outDir\images\yunpan-nginx.tar"   yunpan/nginx:latest

# Copy deploy files
Write-Host "[3/4] Copying deploy files..." -ForegroundColor Yellow
Copy-Item "$root\docker-compose.prod.yml" "$outDir\"
Copy-Item "$root\nginx\nginx.conf" "$outDir\nginx.conf" -ErrorAction SilentlyContinue
Copy-Item "$root\scripts\deploy.sh" "$outDir\"
Copy-Item "$root\scripts\OPS_README.md" "$outDir\README.md" -ErrorAction SilentlyContinue

# Create env template
$envTemplate = @'
DATABASE_URL=postgresql+asyncpg://yunpan:CHANGE_ME@postgres:5432/yunpan
REDIS_URL=redis://:CHANGE_ME@redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=CHANGE_ME
MINIO_BUCKET=yunpan
SECRET_KEY=CHANGE_ME_JWT_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=false
POSTGRES_DB=yunpan
POSTGRES_USER=yunpan
POSTGRES_PASSWORD=CHANGE_ME
REDIS_PASSWORD=CHANGE_ME
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=CHANGE_ME
'@
$envTemplate | Out-File -Encoding utf8 "$outDir\.env.template"

# Package
Write-Host "[4/4] Creating deploy.zip..." -ForegroundColor Yellow
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
