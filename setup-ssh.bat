@echo off
REM ===================================================================
REM TidalAI Companion - Configuración SSH sin contraseña
REM Ejecutar UNA SOLA VEZ para configurar acceso automático
REM ===================================================================

setlocal enabledelayedexpansion

set RASPI_IP=192.168.1.147
set RASPI_USER=pi
set RASPI_PASS=raspi

echo.
echo ========================================
echo  Configuración SSH sin contraseña
echo ========================================
echo.

REM Verificar que ssh está disponible
where ssh >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] SSH no encontrado.
    echo Instala OpenSSH Client desde Configuración de Windows.
    pause
    exit /b 1
)

echo [1/3] Generando clave SSH...
if not exist "%USERPROFILE%\.ssh\id_rsa" (
    ssh-keygen -t rsa -b 4096 -f "%USERPROFILE%\.ssh\id_rsa" -N ""
    echo [OK] Clave SSH generada
) else (
    echo [OK] Clave SSH ya existe
)
echo.

echo [2/3] Copiando clave a Raspberry Pi...
echo.
echo IMPORTANTE: Cuando pida contraseña, escribe: raspi
echo.

REM Crear directorio .ssh en Raspberry Pi si no existe
ssh %RASPI_USER%@%RASPI_IP% "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

REM Copiar clave pública
type "%USERPROFILE%\.ssh\id_rsa.pub" | ssh %RASPI_USER%@%RASPI_IP% "cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Clave copiada correctamente
) else (
    echo.
    echo [ERROR] No se pudo copiar la clave
    pause
    exit /b 1
)
echo.

echo [3/3] Probando conexión sin contraseña...
ssh -o BatchMode=yes %RASPI_USER%@%RASPI_IP% "echo 'Conexión exitosa'"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  ¡Configuración completada!
    echo ========================================
    echo.
    echo Ya puedes usar deploy.bat sin contraseña
    echo.
) else (
    echo.
    echo [ADVERTENCIA] La conexión aún pide contraseña
    echo Verifica que la clave se copió correctamente
    echo.
)

pause
