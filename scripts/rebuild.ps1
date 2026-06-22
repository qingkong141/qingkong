<#
  yunpan rebuild + package script
  Usage: powershell -ExecutionPolicy Bypass -File .\scripts\rebuild.ps1
#>
$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $PSScriptRoot

Write-Host "=== yunpan rebuild & package ===" -ForegroundColor Cyan

Write-Host "[1/3] Stopping old containers..." -ForegroundColor Yellow
Push-Location $root
$null = docker compose -f docker-compose.prod.yml --env-file backend/.env down 2>&1
$null = docker compose down 2>&1
Pop-Location

Write-Host "[2/3] Rebuilding images..." -ForegroundColor Yellow
Push-Location $root
docker compose -f docker-compose.prod.yml --env-file backend/.env build backend 2>&1
if ($LASTEXITCODE -ne 0) { throw "Backend build failed" }
docker compose -f docker-compose.prod.yml --env-file backend/.env build nginx 2>&1
if ($LASTEXITCODE -ne 0) { throw "Nginx build failed" }
Pop-Location

Write-Host "[3/3] Packaging deploy.zip..." -ForegroundColor Yellow
& "$PSScriptRoot\build-package.ps1"
