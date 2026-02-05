@echo off
echo Iniciando TidalAI Local Launcher...
echo.
echo [INFO] Verificando dependencias locales...
pip install flask >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] No se pudo instalar Flask automaticamente.
    echo Ejecuta: pip install flask
    pause
)

echo [INFO] Arrancando motor Flask en localhost:8080...
python "%~dp0tools\launcher.py"
pause
