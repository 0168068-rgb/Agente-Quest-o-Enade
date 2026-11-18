#!/usr/bin/env bash
# Sincronização Automática: OneDrive (Skills/Rules/Plugins) e GitHub (Projetos Antigravity)
set -u

echo "=========================================="
echo "🔄 Sincronização Antigravity iniciada..."
echo "=========================================="

# 1. Detecção do diretório OneDrive montado
ONEDRIVE_DIR=""
for d in "$HOME/onedrive- Hamilcar" "$HOME/OneDrive"; do
  if [ -d "$d" ]; then
    ONEDRIVE_DIR="$d"
    break
  fi
done

if [ -n "$ONEDRIVE_DIR" ]; then
  if mountpoint -q "$ONEDRIVE_DIR" 2>/dev/null; then
    echo "✅ OneDrive montado e ativo em: $ONEDRIVE_DIR"
  else
    echo "⚠️ AVISO: Diretório $ONEDRIVE_DIR encontrado, mas não está montado via FUSE (onedriver)."
  fi
  REMOTO="$ONEDRIVE_DIR/Antigravity_Global_Config"
else
  echo "⚠️ AVISO: Nenhuma pasta OneDrive encontrada em ~/onedrive- Hamilcar ou ~/OneDrive."
  REMOTO=""
fi

# 2. Sincronização de Configurações Globais (Skills, Rules, Plugins)
LOCAL="$HOME/.gemini/config"
if [ -n "$REMOTO" ]; then
  mkdir -p "$REMOTO/skills" "$REMOTO/rules" "$REMOTO/plugins" 2>/dev/null || true
  
  # Se já forem symlinks para o OneDrive, a sincronização é nativa e em tempo real
  if [ -L "$LOCAL/skills" ] && [ -L "$LOCAL/rules" ]; then
    echo "✅ Skills, Rules e Plugins já estão vinculados diretamente ao OneDrive (tempo real)."
  else
    echo "📦 Sincronizando pastas locais de skills e rules via rsync..."
    OPTS=(-au --exclude=.git --exclude=node_modules)
    for p in skills rules plugins; do
      [ -d "$REMOTO/$p" ] && [ -d "$LOCAL/$p" ] && {
        rsync "${OPTS[@]}" "$REMOTO/$p/" "$LOCAL/$p/" 2>/dev/null || true
        rsync "${OPTS[@]}" "$LOCAL/$p/" "$REMOTO/$p/" 2>/dev/null || true
      }
    done
  fi

  # Sincronização do AGENTS.md
  [ -f "$REMOTO/AGENTS.md" ] && [ -f "$LOCAL/AGENTS.md" ] && rsync -au "$REMOTO/AGENTS.md" "$LOCAL/AGENTS.md" 2>/dev/null || true
  [ -f "$LOCAL/AGENTS.md" ] && [ -d "$REMOTO" ] && rsync -au "$LOCAL/AGENTS.md" "$REMOTO/AGENTS.md" 2>/dev/null || true
fi

# 3. Sincronização dos Projetos no GitHub (~/Antigravity)
PROJETO_DIR="$HOME/Antigravity"
if [ -d "$PROJETO_DIR/.git" ]; then
  echo "------------------------------------------"
  echo "🐙 Sincronizando Projetos com o GitHub ($PROJETO_DIR)..."
  cd "$PROJETO_DIR"

  # Verificar e commitar alterações locais pendentes primeiro
  STATUS=$(git status --porcelain)
  if [ -n "$STATUS" ]; then
    echo "📤 Encontradas alterações locais para sincronizar. Gravando..."
    git add .
    COMMIT_MSG="sync: atualização automática ($(date '+%d/%m/%Y %H:%M:%S'))"
    git commit -m "$COMMIT_MSG" 2>/dev/null || true
  fi

  # Puxar novidades remotas com rebase
  echo "📥 Verificando e puxando atualizações do GitHub (git pull --rebase)..."
  if git pull --rebase origin main 2>/dev/null; then
    echo "✅ Repositório local atualizado com o GitHub."
  else
    echo "⚠️ Não foi possível puxar do GitHub (verifique a conexão ou conflitos)."
  fi

  # Enviar para a nuvem se estiver à frente do remoto
  AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
  if [ "$AHEAD" -gt 0 ]; then
    echo "🚀 Enviando $AHEAD commit(s) para o GitHub..."
    if git push origin main 2>/dev/null; then
      echo "✅ Alterações enviadas com sucesso para o GitHub!"
    else
      echo "⚠️ Falha ao enviar para o GitHub (verifique as credenciais ou rede)."
    fi
  else
    echo "✅ Repositório 100% atualizado e alinhado com o GitHub!"
  fi
else
  echo "ℹ️ Repositório $PROJETO_DIR não encontrado ou sem Git inicializado."
fi

echo "=========================================="
echo "🎉 Sincronização concluída com sucesso!"
echo "=========================================="
