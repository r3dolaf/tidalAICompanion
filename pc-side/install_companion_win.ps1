<#
.SYNOPSIS
    TidalAI Companion - Instalador Universal para Windows
    
.DESCRIPTION
    Configura un PC desde cero para recibir audio de la Raspberry Pi (Modo Runtime)
    o para desarrollar código TidalCycles (Modo Studio).

.NOTES
    Requiere ejecutar como Administrador.
#>

param (
    [switch]$FullStudio  # Si se pasa este flag, instala VSCode + Extensiones
)

Write-Host "🎹 TidalAI Companion Installer v1.0" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# 1. Verificar Permisos
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Este script requiere permisos de Administrador."
    Write-Warning "Por favor, click derecho -> Ejecutar como Administrador."
    Break
}

# 2. Instalar Chocolatey (Gestor de Paquetes)
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "-> Instalando Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
} else {
    Write-Host "-> Chocolatey ya está instalado." -ForegroundColor Green
}

# 3. Instalar Core Audio (SuperCollider)
Write-Host "`n-> Verificando SuperCollider..." -ForegroundColor Yellow
choco install supercollider -y
choco install git -y --params "/GitAndUnixToolsOnPath"

# 4. Instalar TidalCycles (Haskell)
Write-Host "`n-> Verificando TidalCycles (Ghcup)..." -ForegroundColor Yellow
if (!(Get-Command ghci -ErrorAction SilentlyContinue)) {
    Write-Host "   Instalando entorno Haskell (esto puede tardar)..." -ForegroundColor Magenta
    choco install ghc cabal -y
    cabal update
    cabal install tidal --lib
} else {
    Write-Host "   Haskell ya está presente." -ForegroundColor Green
    # Asegurar que la librería Tidal está instalada
    cabal install tidal --lib
}

# 5. Instalar SuperDirt (Quark)
Write-Host "`n-> Instalando SuperDirt en SuperCollider..." -ForegroundColor Yellow
# Creamos un script temporal de SC para instalar el Quark
$scInstallScript = @"
Quarks.install("SuperDirt");
0.exit;
"@
$scScriptPath = "$env:TEMP\install_superdirt.scd"
$scInstallScript | Out-File -Encoding UTF8 $scScriptPath

# Buscamos sclang estandar
$sclangPath = "C:\Program Files\SuperCollider-*\sclang.exe"
$resolvedSc = Get-ChildItem $sclangPath | Select-Object -First 1

if ($resolvedSc) {
    Start-Process -FilePath $resolvedSc.FullName -ArgumentList $scScriptPath -Wait
    Write-Host "   SuperDirt instalado/actualizado." -ForegroundColor Green
} else {
    Write-Warning "   No se encontró sclang.exe. Asegúrate de instalar SuperDirt manualmente."
}

# 6. Modo Studio (Opcional)
if ($FullStudio) {
    Write-Host "`n-> [MODO STUDIO] Instalando VS Code..." -ForegroundColor Cyan
    choco install vscode -y
    
    Write-Host "-> Instalando Extensión TidalCycles..." -ForegroundColor Cyan
    code --install-extension tidalcycles.tidalcycles
    
    Write-Host "-> Entorno de Desarrollo listo." -ForegroundColor Green
}

# 7. Copiar Receptor OSC (El Corazón)
Write-Host "`n-> Configurando osc_receiver.scd..." -ForegroundColor Yellow
$scStartupDir = "$env:USERPROFILE\AppData\Local\SuperCollider\sc3plugins" # Ruta estandar aproximada o Startup personal
# Mejor: Usamos la carpeta de Startup File del usuario
$scUserAppSupport = "$env:USERPROFILE\AppData\Local\SuperCollider"
if (!(Test-Path $scUserAppSupport)) { New-Item -ItemType Directory -Force -Path $scUserAppSupport }

$currentDir = Get-Location
$receiverSource = Join-Path $currentDir "osc_receiver.scd"

if (Test-Path $receiverSource) {
    Copy-Item $receiverSource -Destination "$scUserAppSupport\startup.scd" -Force
    Write-Host "   Listener instalado como Startup Script." -ForegroundColor Green
    Write-Host "   ¡SuperCollider escuchará a la Pi automáticamente al abrirse!" -ForegroundColor Green
} else {
    Write-Warning "   No se encontró osc_receiver.scd en la carpeta actual."
}

Write-Host "`n=== INSTALACIÓN COMPLETADA ===" -ForegroundColor Cyan
if ($FullStudio) {
    Write-Host "Ya puedes abrir VS Code y empezar a codear."
} else {
    Write-Host "Abre SuperCollider y déjalo corriendo para recibir audio."
}
Read-Host "Presiona Enter para salir"
