#!/usr/bin/env bash
# ==============================================================================
# Iniciar Google Chrome com o SmartDuck Carregado Automaticamente
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSAO_DIR="$(cd "$SCRIPT_DIR/../src/extensao" && pwd)"

CHROME_BIN="google-chrome"
if ! command -v "$CHROME_BIN" &> /dev/null; then
    if command -v google-chrome-stable &> /dev/null; then
        CHROME_BIN="google-chrome-stable"
    elif command -v chromium &> /dev/null; then
        CHROME_BIN="chromium"
    fi
fi

echo "Iniciando $CHROME_BIN com extensão SmartDuck em segundo plano..."
nohup "$CHROME_BIN" \
    --load-extension="$EXTENSAO_DIR" \
    "https://portal.sophia.com.br" \
    "https://avauni.grupoa.education" \
    "$@" > /dev/null 2>&1 &

echo "Google Chrome iniciado com sucesso! O terminal está livre."
