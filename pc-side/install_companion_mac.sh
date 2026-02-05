#!/bin/bash

# TidalAI Companion - Instalador Universal para macOS
# ----------------------------------------------------
# Configura un Mac para recibir audio de la Raspberry Pi (Runtime)
# o para desarrollar código TidalCycles (Studio).

echo -e "\033[96m🎹 TidalAI Companion Installer v1.0 (macOS)\033[0m"
echo "============================================"

# Modo Studio Flag
FULL_STUDIO=false
if [ "$1" == "--studio" ]; then
    FULL_STUDIO=true
fi

# 1. Verificar Homebrew
if ! command -v brew &> /dev/null; then
    echo -e "\033[93m-> Homebrew no detectado. Instalando...\033[0m"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Añadir a path si es Apple Silicon
    if [ -d "/opt/homebrew/bin" ]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo -e "\033[92m-> Homebrew detectado.\033[0m"
fi

# 2. Instalar SuperCollider
echo -e "\n\033[93m-> Verificando SuperCollider...\033[0m"
if ! brew list --cask supercollider &> /dev/null; then
    brew install --cask supercollider
else
    echo -e "\033[92m   SuperCollider ya instalado.\033[0m"
fi

# 3. Instalar TidalCycles (Haskell)
echo -e "\n\033[93m-> Verificando TidalCycles (GHCup)...\033[0m"
if ! command -v ghci &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://get-ghcup.haskell.org | sh
    # Refresh env
    [ -f "$HOME/.ghcup/env" ] && source "$HOME/.ghcup/env"
    cabal install tidal --lib
else
    echo -e "\033[92m   Haskell ya presente.\033[0m"
    cabal install tidal --lib
fi

# 4. Instalar SuperDirt (Quark)
echo -e "\n\033[93m-> Instalando SuperDirt...\033[0m"
# Script temporal
cat <<EOF > /tmp/install_superdirt.scd
Quarks.install("SuperDirt");
0.exit;
EOF

# Ejecutar sclang
/Applications/SuperCollider.app/Contents/MacOS/sclang /tmp/install_superdirt.scd

# 5. Modo Studio (Opcional)
if [ "$FULL_STUDIO" = true ]; then
    echo -e "\n\033[96m-> [MODO STUDIO] Configurando VS Code...\033[0m"
    if ! brew list --cask visual-studio-code &> /dev/null; then
        brew install --cask visual-studio-code
    fi
    
    echo "-> Instalando extensión TidalCycles..."
    code --install-extension tidalcycles.tidalcycles
    echo -e "\033[92m-> Entorno de Desarrollo listo.\033[0m"
fi

# 6. Copiar Receptor OSC
echo -e "\n\033[93m-> Configurando osc_receiver.scd...\033[0m"
SC_STARTUP_DIR="$HOME/Library/Application Support/SuperCollider"
mkdir -p "$SC_STARTUP_DIR"

if [ -f "./osc_receiver.scd" ]; then
    cp "./osc_receiver.scd" "$SC_STARTUP_DIR/startup.scd"
    echo -e "\033[92m   Listener instalado como Startup Script.\033[0m"
else
    echo -e "\033[91m   No se encontró osc_receiver.scd en el directorio actual.\033[0m"
fi

echo -e "\n\033[96m=== INSTALACIÓN COMPLETADA ===\033[0m"
if [ "$FULL_STUDIO" = true ]; then
    echo "Ya puedes abrir VS Code."
else
    echo "Abre SuperCollider para empezar."
fi
