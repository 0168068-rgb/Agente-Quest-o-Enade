---
name: ava-question-automation
description: Guia e instrução para automação de cadastro em lote de questões acadêmicas no AVA (Grupo A) a partir de planilhas Excel usando Playwright e mutação de modelo Vue.js.
---

# Automação de Inserção de Questões no AVA (Grupo A)

Esta habilidade orienta como executar a automação de inserção de questões acadêmicas em lote na plataforma AVA do Grupo A.

## Arquivos e Localização
- Diretório do Harness: `/home/hamilcar/Antigravity/automacao_avalia_autobatch/`
- Script de Automação (CLI): `/home/hamilcar/Antigravity/automacao_avalia_autobatch/src/automate_questions.py`
- Aplicativo Gráfico (GUI): `/home/hamilcar/Antigravity/automacao_avalia_autobatch/src/app_avalia_gui.py`
- Pasta de Planilhas: `/home/hamilcar/Antigravity/automacao_avalia_autobatch/planilhas/`
- Scripts de Submissão por Disciplina: `/home/hamilcar/Antigravity/automacao_avalia_autobatch/disciplinas/`
- Ambiente Virtual Python: `/home/hamilcar/Antigravity/venv`

## Estrutura Exigida da Planilha Excel (`.xlsx`)
As planilhas devem conter as seguintes colunas:
1. `Ordem`: Número de identificação da questão (1, 2, 3...).
2. `Enunciado`: Texto do enunciado da questão.
3. `Resposta 1` a `Resposta 5`: Textos das cinco alternativas.
4. `Resposta certa`: Letra (`A`, `B`, `C`, `D`, `E`) ou Número (`1`, `2`, `3`, `4`, `5`) indicando a alternativa correta.
5. `Feedback`: Texto explicativo da resolução da questão.

*(Obs: Se a coluna `Resposta certa` for omitida, o script tenta extrair automaticamente a letra correta do campo `Feedback`)*

## Como Executar
1. Pelo terminal interativo (CLI):
   ```bash
   cd /home/hamilcar/Antigravity
   source venv/bin/activate
   python3 automacao_avalia_autobatch/src/automate_questions.py [caminho_da_planilha.xlsx]
   ```
2. Pela Interface Gráfica (GUI):
   ```bash
   cd /home/hamilcar/Antigravity
   source venv/bin/activate
   python3 automacao_avalia_autobatch/src/app_avalia_gui.py
   ```
2. Fluxo de uso com o usuário:
   - O script lista as planilhas disponíveis no diretório.
   - O Chromium abre na página de login do AVA.
   - O usuário faz login e navega até a tela do Quiz no AVA, abrindo o modal de edição de questão.
   - No terminal, executa-se o comando `test` para preencher a 1ª questão.
   - Após validação manual da 1ª questão (salvar e abrir o próximo modal), executa-se o comando `run` informando a ordem inicial (ex: 2).
