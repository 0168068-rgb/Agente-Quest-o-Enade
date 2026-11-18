#!/usr/bin/env bash
set -e

# ==============================================================================
# SmartFox Autônomo 11.2 - Instalador Nativo para Linux
# ==============================================================================

echo "============================================================"
echo "        🦊 Instalação do SmartFox Autônomo 11.2 (Linux)      "
echo "============================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EXTENSAO_DIR="$PROJECT_ROOT/src/extensao"
TARGET_DIR="$HOME/.local/share/smartfox/extensao"
ICON_SOURCE="$EXTENSAO_DIR/icons/icon-128.png"
DESKTOP_DIR="$HOME/Área de trabalho"

echo "[1/4] Preparando diretórios locais..."
mkdir -p "$HOME/.local/share/smartfox"
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$HOME/.local/share/icons/hicolor/128x128/apps"

# Link simbólico para a extensão
if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
fi
ln -s "$EXTENSAO_DIR" "$TARGET_DIR"
echo "  -> Extensão vinculada em: $TARGET_DIR"

echo "[2/4] Instalando ícones e atalhos..."
cp "$ICON_SOURCE" "$HOME/.local/share/icons/hicolor/128x128/apps/smartfox.png"

LAUNCHER_FILE="$HOME/.local/share/applications/smartfox.desktop"
cat <<EOF > "$LAUNCHER_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=SmartFox (AvaliA)
Comment=Ferramentas do professor no AvaliA, acervo local e correção
Exec=google-chrome --load-extension="$TARGET_DIR" https://avalia.grupoa.com.br
Icon=smartfox
Terminal=false
Categories=Education;Office;Utility;
Keywords=avalia;questoes;grupoa;smartfox;
EOF
chmod +x "$LAUNCHER_FILE"

if [ -d "$DESKTOP_DIR" ]; then
    cp "$LAUNCHER_FILE" "$DESKTOP_DIR/smartfox.desktop"
    chmod +x "$DESKTOP_DIR/smartfox.desktop"
    echo "  -> Atalho criado na Área de Trabalho: $DESKTOP_DIR/smartfox.desktop"
fi

echo "[3/4] Verificando navegador Google Chrome..."
if command -v google-chrome &> /dev/null; then
    CHROME_BIN="google-chrome"
elif command -v google-chrome-stable &> /dev/null; then
    CHROME_BIN="google-chrome-stable"
elif command -v chromium &> /dev/null; then
    CHROME_BIN="chromium"
else
    echo "  [AVISO] Google Chrome não encontrado no PATH."
fi

echo "[4/4] Concluído!"
echo ""
echo "============================================================"
echo "       🎉 SmartFox Autônomo 11.2 Preparado com Sucesso!     "
echo "============================================================"
echo ""
echo "Para ativar no Chrome:"
echo "  1. Acesse: chrome://extensions"
echo "  2. Ative 'Modo do desenvolvedor'"
echo "  3. Clique em 'Carregar sem compactação'"
echo "  4. Selecione a pasta:"
echo "     $TARGET_DIR"
echo "     (ou /home/hamilcar/Antigravity/smartfox/src/extensao)"
echo ""
echo "Depois, basta voltar na aba do AvaliA e pressionar F5 (Recarregar)."
echo "============================================================"
