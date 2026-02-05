@echo off
chcp 65001 >nul
REM ===================================================================
REM Script de Limpieza - TidalAI Companion
REM Elimina archivos temporales y obsoletos
REM ===================================================================

echo.
echo ========================================
echo  Limpieza de Archivos Obsoletos
echo ========================================
echo.

set PROJECT_DIR=C:\Users\alfredo\Desktop\tidalai-companion

echo Archivos que se eliminaran:
echo.
echo [Scripts Obsoletos]
echo   - deploy.ps1 (reemplazado por deploy.bat)
echo   - transfer-to-raspi.ps1 (reemplazado por deploy.bat)
echo   - update-raspi.ps1 (obsoleto)
echo   - update-favorites.ps1 (obsoleto)
echo   - extract-from-project.bat (no se usa)
echo   - pi@192.168.1.1 (archivo temporal)
echo.
echo [Archivos Temporales del Corpus]
echo   - extracted_patterns.txt (version antigua)
echo   - extracted_patterns_v2.txt (duplicado)
echo   - extracted_favorites.json (temporal)
echo   - patterns_minimal.txt (no se usa)
echo   - superdirt_samples.txt (no se usa)
echo.
echo NOTA: Se mantendran:
echo   - patterns.txt (corpus base)
echo   - deploy.bat
echo   - setup-ssh.bat
echo   - extract-patterns-interactive.bat
echo.

set /p CONFIRM="Continuar con la limpieza? (S/N): "

if /i NOT "%CONFIRM%"=="S" (
    echo.
    echo Limpieza cancelada.
    pause
    exit /b 0
)

echo.
echo Eliminando archivos...
echo.

REM Scripts obsoletos
if exist "%PROJECT_DIR%\deploy.ps1" (
    del "%PROJECT_DIR%\deploy.ps1"
    echo [OK] deploy.ps1 eliminado
)

if exist "%PROJECT_DIR%\transfer-to-raspi.ps1" (
    del "%PROJECT_DIR%\transfer-to-raspi.ps1"
    echo [OK] transfer-to-raspi.ps1 eliminado
)

if exist "%PROJECT_DIR%\update-raspi.ps1" (
    del "%PROJECT_DIR%\update-raspi.ps1"
    echo [OK] update-raspi.ps1 eliminado
)

if exist "%PROJECT_DIR%\update-favorites.ps1" (
    del "%PROJECT_DIR%\update-favorites.ps1"
    echo [OK] update-favorites.ps1 eliminado
)

if exist "%PROJECT_DIR%\extract-from-project.bat" (
    del "%PROJECT_DIR%\extract-from-project.bat"
    echo [OK] extract-from-project.bat eliminado
)

if exist "%PROJECT_DIR%\pi@192.168.1.1" (
    del "%PROJECT_DIR%\pi@192.168.1.1"
    echo [OK] pi@192.168.1.1 eliminado
)

REM Archivos temporales del corpus
if exist "%PROJECT_DIR%\examples\corpus\extracted_patterns.txt" (
    del "%PROJECT_DIR%\examples\corpus\extracted_patterns.txt"
    echo [OK] extracted_patterns.txt eliminado
)

if exist "%PROJECT_DIR%\examples\corpus\extracted_patterns_v2.txt" (
    del "%PROJECT_DIR%\examples\corpus\extracted_patterns_v2.txt"
    echo [OK] extracted_patterns_v2.txt eliminado
)

if exist "%PROJECT_DIR%\examples\corpus\extracted_favorites.json" (
    del "%PROJECT_DIR%\examples\corpus\extracted_favorites.json"
    echo [OK] extracted_favorites.json eliminado
)

if exist "%PROJECT_DIR%\examples\corpus\patterns_minimal.txt" (
    del "%PROJECT_DIR%\examples\corpus\patterns_minimal.txt"
    echo [OK] patterns_minimal.txt eliminado
)

if exist "%PROJECT_DIR%\examples\corpus\superdirt_samples.txt" (
    del "%PROJECT_DIR%\examples\corpus\superdirt_samples.txt"
    echo [OK] superdirt_samples.txt eliminado
)

echo.
echo ========================================
echo  Limpieza Completada
echo ========================================
echo.
echo Archivos mantenidos:
echo   - README.md
echo   - QUICKSTART.md
echo   - deploy.bat
echo   - setup-ssh.bat
echo   - extract-patterns-interactive.bat
echo   - examples\corpus\patterns.txt
echo   - Todos los directorios (docs, raspberry-pi, tools, etc.)
echo.

pause
