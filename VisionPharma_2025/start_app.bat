@echo off
echo ================================================
echo    VisionPharma 2025 - Iniciando Aplicacion
echo ================================================
echo.

echo [1/2] Activando entorno virtual...
call .\venv311\Scripts\Activate.ps1

echo.
echo [2/2] Iniciando aplicacion web Flask...
echo.
echo Accede a: http://localhost:5000
echo Presiona Ctrl+C para detener la aplicacion
echo.

python app.py

pause
