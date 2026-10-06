@echo off
title Smart Barrel Copilot - Visual Cellar Cockpit
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   SMART BARREL COPILOT - Visual Cellar Cockpit
echo   Iniciando servidor en http://localhost:8070
echo ========================================================
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.

start "" http://localhost:8070/index.html
python "dashboard\server.py"
pause
