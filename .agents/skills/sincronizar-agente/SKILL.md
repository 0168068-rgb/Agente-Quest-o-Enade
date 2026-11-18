---
name: sincronizar-agente
description: Use esta skill sempre que o usuário pedir para "sincronizar", "sincronizar agente", "sincronizar computador", "sincronizar os antigravity", "sync" ou "salvar e enviar alterações".
---

# Skill: Sincronização Automática dos Computadores

Sincroniza habilidades (`skills/`), regras (`rules/`) e `AGENTS.md` entre `~/.gemini/config` e a pasta do OneDrive `~/OneDrive/Antigravity_Global_Config`, que é compartilhada entre o Computador A e o Computador B.

---

## 1. Gatilhos de Ativação
- *"sincronizar"* / *"sincronizar agente"* / *"sincronizar computadores"* / *"sincronizar os antigravity"*
- *"sync"* / *"salvar e sincronizar"*
- *"enviar para o outro computador"*

---

## 2. Fluxo de Sincronização

1. **Executar o script** (sincronização bidirecional: o arquivo mais recente vence; nada é apagado):
   ```bash
   bash ~/.gemini/config/skills/sincronizar-agente/sync.sh
   ```
   `~/OneDrive` é montado pelo `onedriver` (FUSE): gravar ali já envia à nuvem.

2. **Projetos com Git** em `~/projetos_Antigravity/*` (opcional): `git pull --rebase` e `git push` em cada repositório com alterações.

3. **Confirmar ao Usuário**: informar o resultado, incluindo avisos de falha do OneDrive ou de autenticação do Git.
