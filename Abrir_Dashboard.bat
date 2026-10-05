@echo off
title Smart Barrel Copilot - Visual Cellar Cockpit
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   🪵 Iniciando Visual Cockpit · Smart Barrel Copilot
echo ========================================================
echo Abriendo en tu navegador predeterminado...
echo Localhost: http://localhost:8070/index.html
echo.

python "dashboard\server.py"
pause
