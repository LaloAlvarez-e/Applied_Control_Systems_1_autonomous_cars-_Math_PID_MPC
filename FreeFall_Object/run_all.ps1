# Complete workflow script - Build and Run Everything
# Executes from FreeFall_Object root directory

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Complete Simulation Workflow" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

# Step 1: Build C simulation
Write-Host "[1/4] Building C simulation..." -ForegroundColor Yellow
& .\build.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Run simulation
Write-Host "`n[2/4] Running simulation (generates 550+ CSV files)..." -ForegroundColor Yellow
& .\build\bin\freefall_object.exe

# Step 3: Run comprehensive analysis
Write-Host "`n[3/4] Analyzing results..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe scripts\analyze_comprehensive.py

# Step 4: Generate visualizations
Write-Host "`n[4/4] Generating angle comparison plots..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe scripts\visualize_angles.py

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "Complete! All simulations and analyses finished." -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green

Write-Host "`nGenerated files:" -ForegroundColor Cyan
Write-Host "  - csv_data/ (550+ simulation files)" -ForegroundColor White
Write-Host "  - plots/comprehensive_analysis.png" -ForegroundColor White
Write-Host "  - plots/angle_specific_analysis.png" -ForegroundColor White
Write-Host "  - plots/angles/angle_comparison.png" -ForegroundColor White
Write-Host "  - plots/angles/individual/ (10 detail plots)" -ForegroundColor White
Write-Host "  - analysis_results.csv" -ForegroundColor White

Write-Host "`nView results with:" -ForegroundColor Cyan
Write-Host "  Start-Process plots\comprehensive_analysis.png" -ForegroundColor White
