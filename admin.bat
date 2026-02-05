@echo off
REM ===================================================================
REM Launcher - TidalAI Admin Panel
REM Abre el panel de administracion web
REM ===================================================================

echo Abriendo TidalAI Admin Panel (Control Center)...
REM IP de la Raspberry Pi (detectada del deploy anterior)
start "" "http://192.168.1.147:5000/admin"
