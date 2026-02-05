@echo off
REM ===================================================================
REM TidalAI Companion - Deploy Robusto v2
REM Transfiere archivos con reintentos y verificaciones
REM ===================================================================

setlocal enabledelayedexpansion

REM Configuración de Red
set RASPI_IP=192.168.1.147
set RASPI_USER=pi
set PROJECT_DIR=%~dp0
set MAX_RETRIES=2
set CONNECT_TIMEOUT=5

echo.
echo ========================================
echo  TidalAI Companion - Smart Deploy
echo ========================================
echo.

REM 1. Verificar Conectividad
echo [1/5] Verificando red (%RASPI_IP%)...
ping -n 1 -w 2000 %RASPI_IP% >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se detecta la Raspberry Pi en %RASPI_IP%
    echo Sugerencias:
    echo   - Verifica que esté encendida.
    echo   - Verifica que estés en la misma red WiFi.
    pause
    exit /b 1
)
echo [OK] Conexión establecida
echo.

REM 2. Preparar Entorno Remoto (Crear carpetas si faltan)
echo [2/5] Preparando carpetas remotas...
ssh -o ConnectTimeout=%CONNECT_TIMEOUT% -o BatchMode=yes %RASPI_USER%@%RASPI_IP% "mkdir -p ~/tidalai-companion/raspberry-pi/web/static ~/tidalai-companion/raspberry-pi/web/templates ~/tidalai-companion/raspberry-pi/generator ~/tidalai-companion/examples/corpus" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Primer intento fallido, probando con contraseña...
    ssh %RASPI_USER%@%RASPI_IP% "mkdir -p ~/tidalai-companion/raspberry-pi/web/static ~/tidalai-companion/raspberry-pi/web/templates ~/tidalai-companion/raspberry-pi/generator ~/tidalai-companion/examples/corpus"
)

REM 3. Definir lista de archivos a transferir
echo.
echo [3/5] Sincronizando archivos...

REM Sincronización Recursiva Inteligente
REM Copia todo el contenido de la carpeta 'raspberry-pi' manteniendo estructura
echo [INFO] Sincronizando carpeta completa 'raspberry-pi'...

scp -r -o ConnectTimeout=%CONNECT_TIMEOUT% -o BatchMode=yes "%PROJECT_DIR%raspberry-pi\*" %RASPI_USER%@%RASPI_IP%:~/tidalai-companion/raspberry-pi/

echo [INFO] Sincronizando corpus purificado...
scp -o ConnectTimeout=%CONNECT_TIMEOUT% -o BatchMode=yes "%PROJECT_DIR%examples\corpus\patterns.txt" %RASPI_USER%@%RASPI_IP%:~/tidalai-companion/examples/corpus/patterns.txt

echo [INFO] Sincronizando instaladores (pc-side)...
scp -r -o ConnectTimeout=%CONNECT_TIMEOUT% -o BatchMode=yes "%PROJECT_DIR%pc-side\*" %RASPI_USER%@%RASPI_IP%:~/tidalai-companion/pc-side/

if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Reintentando modo interactivo...
    scp -r -o ConnectTimeout=%CONNECT_TIMEOUT% "%PROJECT_DIR%raspberry-pi\*" %RASPI_USER%@%RASPI_IP%:~/tidalai-companion/raspberry-pi/
    scp -o ConnectTimeout=%CONNECT_TIMEOUT% "%PROJECT_DIR%examples\corpus\patterns.txt" %RASPI_USER%@%RASPI_IP%:~/tidalai-companion/examples/corpus/patterns.txt
    scp -r -o ConnectTimeout=%CONNECT_TIMEOUT% "%PROJECT_DIR%pc-side\*" %RASPI_USER%@%RASPI_IP%:~/tidalai-companion/pc-side/
)

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Falló la sincronización masiva.
    pause
    exit /b 1
)

echo.
echo [OK] Sincronización completada
echo.

REM 4. Reiniciar Servicio
echo [4/5] Reiniciando servicio tidalai...
ssh -o ConnectTimeout=%CONNECT_TIMEOUT% -o BatchMode=yes %RASPI_USER%@%RASPI_IP% "sudo systemctl restart tidalai.service" 2>nul
if %ERRORLEVEL% NEQ 0 (
    ssh %RASPI_USER%@%RASPI_IP% "sudo systemctl restart tidalai.service"
)

REM 5. Verificación Final
echo [5/5] Verificando estado...
timeout /t 2 >nul
ssh -o ConnectTimeout=%CONNECT_TIMEOUT% -o BatchMode=yes %RASPI_USER%@%RASPI_IP% "sudo systemctl is-active tidalai.service" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [EXITO] Sistema ONLINE y operativo
    echo URL: http://%RASPI_IP%:5000
    echo.
    echo NOTA: Si cambiaste index.html/js, recarga con Ctrl+Shift+R
) else (
    echo.
    echo [ADVERTENCIA] El servicio no parece estar activo.
    echo Revisa logs con: ssh pi@%RASPI_IP% "journalctl -u tidalai -n 20"
)

pause
exit /b 0

REM =======================================================
REM FUNCION AUXILIAR: SendFile
REM =======================================================
:SendFile
set "LOCAL_PATH=%~1"
set "REMOTE_PATH=%~2"
set "FILENAME=%~nx1"

echo   - %FILENAME%
REM Intento 1: BatchMode (rápido, clave SSH)
scp -o ConnectTimeout=%CONNECT_TIMEOUT% -o BatchMode=yes -q "%LOCAL_PATH%" %RASPI_USER%@%RASPI_IP%:%REMOTE_PATH% 2>nul
if %ERRORLEVEL% EQU 0 exit /b 0

REM Intento 2: Interactivo (pide password si falla clave)
scp -o ConnectTimeout=%CONNECT_TIMEOUT% "%LOCAL_PATH%" %RASPI_USER%@%RASPI_IP%:%REMOTE_PATH%
if %ERRORLEVEL% NEQ 0 (
    echo     [!] Falló envío de %FILENAME%
)
exit /b 0
