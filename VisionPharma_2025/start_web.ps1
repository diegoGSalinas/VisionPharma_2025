# start_web.ps1

# Obtiene la ruta de la carpeta raíz del proyecto (D:\git\VisionPharma_2025)
$CurrentDir = (Get-Item -Path $PSScriptRoot).FullName

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   VisionPharma 2025 - Iniciando Web App 2" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Activando entorno virtual..." -ForegroundColor Yellow
# 1. Activación: Usamos la ruta y el operador de llamada (&) que probaste exitosamente.
& "$CurrentDir\venv311\Scripts\Activate.ps1"

# 2. Navegar a la carpeta del servidor web
Write-Host "[2/3] Cambiando directorio a web_interface..." -ForegroundColor Yellow
Set-Location "$CurrentDir\"

# 3. Ejecutar la aplicación Flask
Write-Host ""
Write-Host "[3/3] Iniciando aplicacion web Flask (app2.py)..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Accede a: http://localhost:5000" -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener la aplicacion" -ForegroundColor Green
Write-Host ""

python app2.py