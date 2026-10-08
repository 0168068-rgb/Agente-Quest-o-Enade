#!/bin/bash
set -e

# Define directories
SRC_TAR="/home/hamilcar/Downloads/Antigravity.tar.gz"
TARGET_DIR="/usr/share/antigravity"
BACKUP_DIR="/usr/share/antigravity.bak"
TEMP_DIR="/tmp/antigravity_update"

echo "Iniciando atualização do Antigravity IDE..."

# Verificar se o arquivo baixado existe
if [ ! -f "$SRC_TAR" ]; then
    echo "Erro: O arquivo baixado não foi encontrado em $SRC_TAR"
    exit 1
fi

echo "Criando diretório temporário..."
mkdir -p "$TEMP_DIR"

echo "Extraindo arquivos do pacote..."
tar -xzf "$SRC_TAR" -C "$TEMP_DIR"

# Verificar se a pasta extraída tem a estrutura esperada
EXTRACTED_SUBDIR="$TEMP_DIR/Antigravity-x64"
if [ ! -d "$EXTRACTED_SUBDIR" ]; then
    echo "Erro: Estrutura da pasta extraída inválida. Esperada: $EXTRACTED_SUBDIR"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Remover backup anterior se existir
if [ -d "$BACKUP_DIR" ]; then
    echo "Removendo backup antigo..."
    sudo rm -rf "$BACKUP_DIR"
fi

# Fazer backup da instalação atual
if [ -d "$TARGET_DIR" ]; then
    echo "Criando backup da instalação atual em $BACKUP_DIR..."
    sudo mv "$TARGET_DIR" "$BACKUP_DIR"
fi

# Mover a nova versão para o local correto
echo "Instalando nova versão em $TARGET_DIR..."
sudo mv "$EXTRACTED_SUBDIR" "$TARGET_DIR"

# Restaurar a pasta bin contendo o wrapper da CLI se ele não veio no novo pacote
if [ -d "$BACKUP_DIR/bin" ] && [ ! -d "$TARGET_DIR/bin" ]; then
    echo "Restaurando o wrapper da CLI (bin/antigravity)..."
    sudo cp -r "$BACKUP_DIR/bin" "$TARGET_DIR/bin"
fi

# Limpar arquivos temporários
echo "Limpando arquivos temporários..."
rm -rf "$TEMP_DIR"

# Ajustar permissões de execução dos binários
echo "Ajustando permissões de execução..."
sudo chmod +x "$TARGET_DIR/antigravity"
if [ -f "$TARGET_DIR/bin/antigravity" ]; then
    sudo chmod +x "$TARGET_DIR/bin/antigravity"
fi

# Ajustar permissões do chrome-sandbox (obrigatório para aplicativos Electron no Linux)
if [ -f "$TARGET_DIR/chrome-sandbox" ]; then
    sudo chown root:root "$TARGET_DIR/chrome-sandbox"
    sudo chmod 4755 "$TARGET_DIR/chrome-sandbox"
fi

echo ""
echo "=========================================="
echo " Atualização concluída com sucesso!"
echo " Você já pode iniciar o Antigravity IDE."
echo "=========================================="
echo ""
