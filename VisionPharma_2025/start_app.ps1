Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   VisionPharma 2025 - Iniciando Aplicacion" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Activando entorno virtual..." -ForegroundColor Yellow
& .\venv311\Scripts\Activate.ps1

Write-Host ""
Write-Host "[2/2] Iniciando aplicacion web Flask..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Accede a: http://localhost:5000" -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener la aplicacion" -ForegroundColor Green
Write-Host ""

python app.py
