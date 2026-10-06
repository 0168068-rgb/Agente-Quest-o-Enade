---
name: sincronizar-agente
description: Use esta skill sempre que o usuário pedir para "sincronizar agente", "sincronizar computador", "sync" ou "salvar e enviar alterações".
---

# Skill: Sincronização Automática dos Computadores

Esta skill sincroniza automaticamente o repositório de projetos, habilidades e regras entre o Computador A e o Computador B.

---

## 1. Gatilhos de Ativação
- *"sincronizar agente"* / *"sincronizar computadores"*
- *"sync"* / *"salvar e sincronizar"*
- *"enviar para o outro computador"*

---

## 2. Fluxo de Sincronização
Quando ativada, o agente deve executar os seguintes passos no terminal:

1. **Puxar Atualizações da Nuvem**:
   ```bash
   cd ~/Antigravity && git pull --rebase origin main
   ```

2. **Salvar e Enviar Alterações Locais**:
   ```bash
   cd ~/Antigravity && git add . && git commit -m "auto-sync: atualizacao automatica do agente" && git push origin main
   ```

3. **Confirmar ao Usuário**:
   Informar que o projeto, habilidades e regras foram 100% sincronizados com o GitHub e OneDrive, estando prontos para uso no outro computador!
