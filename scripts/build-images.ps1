# Build Podman images for Sentinel ML - PowerShell

$ErrorActionPreference = "Stop"

Write-Host "Building Sentinel Podman images..." -ForegroundColor Cyan
Write-Host ""

# Ensure we're in project root
Set-Location (Split-Path $PSScriptRoot -Parent)

# Build inference API image
Write-Host "Building inference API image..." -ForegroundColor Yellow
podman build -f infra\Dockerfile.inference -t sentinel-inference:latest .
Write-Host "[OK] sentinel-inference:latest built" -ForegroundColor Green

# Build consumer image
Write-Host ""
Write-Host "Building consumer image..." -ForegroundColor Yellow
podman build -f infra\Dockerfile.consumer -t sentinel-consumer:latest .
Write-Host "[OK] sentinel-consumer:latest built" -ForegroundColor Green

# Load into Minikube if running
try {
    $status = minikube status 2>$null
    if ($status) {
        Write-Host ""
        Write-Host "Loading images into Minikube..." -ForegroundColor Yellow
        minikube image load sentinel-inference:latest
        minikube image load sentinel-consumer:latest
        Write-Host "[OK] Images loaded into Minikube" -ForegroundColor Green
    }
} catch {
    Write-Host "[INFO] Minikube not running, skipping image load" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[SUCCESS] All images built successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Images:" -ForegroundColor White
Write-Host "  - sentinel-inference:latest"
Write-Host "  - sentinel-consumer:latest"
