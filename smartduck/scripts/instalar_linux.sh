#!/usr/bin/env bash
set -e

# ==============================================================================
# SmartDuck 1.9.0 - Instalador Nativo para Linux
# ==============================================================================

echo "============================================================"
echo "          🦆 Instalação do SmartDuck 1.9.0 para Linux       "
echo "============================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EXTENSAO_DIR="$PROJECT_ROOT/src/extensao"
TARGET_DIR="$HOME/.local/share/smartduck/extensao"
ICON_SOURCE="$EXTENSAO_DIR/icons/128.png"
DESKTOP_DIR="$HOME/Área de trabalho"

echo "[1/4] Preparando diretórios locais..."
mkdir -p "$HOME/.local/share/smartduck"
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$HOME/.local/share/icons/hicolor/128x128/apps"

# Link simbólico para a extensão (permite que edições no Antigravity reflitam no Chrome)
if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
fi
ln -s "$EXTENSAO_DIR" "$TARGET_DIR"
echo "  -> Extensão vinculada em: $TARGET_DIR"

echo "[2/4] Instalando ícones e atalhos..."
cp "$ICON_SOURCE" "$HOME/.local/share/icons/hicolor/128x128/apps/smartduck.png"

# Criar lançador .desktop
LAUNCHER_FILE="$HOME/.local/share/applications/smartduck.desktop"
cat <<EOF > "$LAUNCHER_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=SmartDuck (SophiA & AVA)
Comment=Lançamento e conferência de notas SophiA e AVA
Exec=google-chrome --load-extension="$TARGET_DIR" https://portal.sophia.com.br
Icon=smartduck
Terminal=false
Categories=Education;Office;Utility;
Keywords=sophia;ava;notas;enade;smartduck;
EOF
chmod +x "$LAUNCHER_FILE"

if [ -d "$DESKTOP_DIR" ]; then
    cp "$LAUNCHER_FILE" "$DESKTOP_DIR/smartduck.desktop"
    chmod +x "$DESKTOP_DIR/smartduck.desktop"
    echo "  -> Atalho criado na Área de Trabalho: $DESKTOP_DIR/smartduck.desktop"
fi

echo "[3/4] Verificando navegador Google Chrome..."
if command -v google-chrome &> /dev/null; then
    CHROME_BIN="google-chrome"
elif command -v google-chrome-stable &> /dev/null; then
    CHROME_BIN="google-chrome-stable"
elif command -v chromium &> /dev/null; then
    CHROME_BIN="chromium"
else
    echo "  [AVISO] Google Chrome não encontrado no PATH. Instale-o para usar o SmartDuck."
    CHROME_BIN=""
fi

echo "[4/4] Finalizando configuração..."
echo ""
echo "============================================================"
echo "        🎉 SmartDuck 1.9.0 Instalado com Sucesso!           "
echo "============================================================"
echo ""
echo "Para ativar no Chrome (apenas na 1ª vez):"
echo "  1. Abra o Chrome e vá para:  chrome://extensions"
echo "  2. Ative a chave 'Modo do desenvolvedor' (no canto superior direito)"
echo "  3. Clique em 'Carregar sem compactação'"
echo "  4. Selecione a pasta:"
echo "     $TARGET_DIR"
echo ""
echo "Dica: Você também pode abrir o Chrome diretamente com o SmartDuck"
echo "executando: $SCRIPT_DIR/executar_chrome_smartduck.sh"
echo "============================================================"
