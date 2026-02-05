@echo off
chcp 65001 >nul
REM ===================================================================
REM Extractor Interactivo de Patrones TidalCycles
REM Ejecutar sin parametros - El script hace todas las preguntas
REM ===================================================================

setlocal enabledelayedexpansion

set PROJECT_DIR=%~dp0

echo.
echo ========================================
echo  Extractor de Patrones TidalCycles
echo ========================================
echo.

REM Verificar Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no encontrado
    pause
    exit /b 1
)

REM Pregunta 1: Directorio a escanear
echo [Paso 1/5] Directorio a escanear
echo.
echo Directorio por defecto: C:\Users\alfredo\Desktop\tidal
echo.
set /p CUSTOM_DIR="Presiona Enter para usar el default o escribe otra ruta: "

if "%CUSTOM_DIR%"=="" (
    set TIDAL_DIR=C:\Users\alfredo\Desktop\tidal
) else (
    set TIDAL_DIR=%CUSTOM_DIR%
)

if not exist "%TIDAL_DIR%" (
    echo.
    echo [ERROR] El directorio no existe: %TIDAL_DIR%
    pause
    exit /b 1
)

echo.
echo [OK] Usando: %TIDAL_DIR%
echo.
pause

REM Pregunta 2: Modo interactivo
echo.
echo [Paso 2/5] Modo de clasificacion
echo.
echo Quieres revisar manualmente los patrones "unknown"?
echo (Te preguntara por cada patron no clasificado automaticamente)
echo.
set /p INTERACTIVE="(S/N): "

if /i "%INTERACTIVE%"=="S" (
    set INTERACTIVE_FLAG=--interactive
    echo [OK] Modo interactivo activado
) else (
    set INTERACTIVE_FLAG=
    echo [OK] Modo automatico
)

echo.
pause

REM Pregunta 3: Formato de salida
echo.
echo [Paso 3/5] Formato de salida
echo.
echo 1. Corpus (archivo .txt para entrenar modelo)
echo 2. Favoritos (archivo .json para favoritos)
echo.
set /p FORMAT_CHOICE="Elige opcion (1/2): "

if "%FORMAT_CHOICE%"=="2" (
    set FORMAT=favorites
    set OUTPUT_FILE=examples\corpus\extracted_favorites.json
    echo [OK] Formato: Favoritos JSON
) else (
    set FORMAT=corpus
    set OUTPUT_FILE=examples\corpus\extracted_patterns.txt
    echo [OK] Formato: Corpus TXT
)

echo.
pause

REM Pregunta 4: Añadir al corpus
echo.
echo [Paso 4/5] Anadir al corpus base
echo.
echo Anadir automaticamente los patrones al corpus base?
echo (Se anadiran a examples\corpus\patterns.txt)
echo.
set /p ADD_CORPUS="(S/N): "

if /i "%ADD_CORPUS%"=="S" (
    set ADD_FLAG=--add-to-corpus
    echo [OK] Se anadira al corpus
) else (
    set ADD_FLAG=
    echo [OK] No se anadira automaticamente
)

echo.
pause

REM Pregunta 5: Re-entrenar
echo.
echo [Paso 5/5] Re-entrenar modelo
echo.
echo Preguntar si re-entrenar el modelo despues de extraer?
echo (Tendras que hacerlo manualmente desde la web)
echo.
set /p TRAIN="(S/N): "

if /i "%TRAIN%"=="S" (
    set TRAIN_FLAG=--auto-train
    echo [OK] Preguntara al final
) else (
    set TRAIN_FLAG=
    echo [OK] No preguntara
)

echo.
echo ========================================
echo  Configuración completada
echo ========================================
echo.
echo Directorio: %TIDAL_DIR%
echo Modo: %INTERACTIVE_FLAG%
echo Formato: %FORMAT%
echo Añadir corpus: %ADD_FLAG%
echo Re-entrenar: %TRAIN_FLAG%
echo.
echo Presiona cualquier tecla para comenzar la extracción...
pause >nul

REM Ejecutar extractor
echo.
echo ========================================
echo  Extrayendo patrones...
echo ========================================
echo.

python "%PROJECT_DIR%tools\extract-patterns.py" "%TIDAL_DIR%" ^
    --output "%OUTPUT_FILE%" ^
    --format %FORMAT% ^
    %INTERACTIVE_FLAG% ^
    %ADD_FLAG% ^
    %TRAIN_FLAG%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Error durante la extracción
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Extracción completada
echo ========================================
echo.
echo Archivo generado: %OUTPUT_FILE%
echo.

REM Si no se añadió al corpus, preguntar ahora
if /i NOT "%ADD_CORPUS%"=="S" (
    echo Quieres anadir estos patrones al corpus ahora?
    set /p ADD_NOW="(S/N): "
    
    if /i "!ADD_NOW!"=="S" (
        type "%OUTPUT_FILE%" >> examples\corpus\patterns.txt
        echo [OK] Patrones anadidos al corpus
    )
)

echo.
echo Proximos pasos:
echo   1. Ejecuta: deploy.bat
echo   2. Abre: http://192.168.1.147:5000
echo   3. Click: "Re-entrenar Modelo"
echo.

pause
