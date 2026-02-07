# Build script for FreeFall_Object project
# Builds C simulation from code/ directory

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Building FreeFall_Object - Train Catching Ball Simulation" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

# Navigate to build directory
if (-not (Test-Path "build")) {
    Write-Host "Creating build directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "build" | Out-Null
}

Set-Location "build"

# Configure CMake (source is in ../code/)
Write-Host "Configuring CMake..." -ForegroundColor Yellow
cmake ..\code

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nCMake configuration failed!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

# Build
Write-Host "`nBuilding..." -ForegroundColor Yellow
cmake --build .

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "Build successful!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "`nExecutable: .\build\bin\freefall_object.exe" -ForegroundColor Cyan
Write-Host "Run with: .\build\bin\freefall_object.exe`n" -ForegroundColor Cyan
