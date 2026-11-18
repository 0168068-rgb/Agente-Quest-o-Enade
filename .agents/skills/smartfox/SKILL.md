---
name: smartfox
description: Use esta skill sempre que o usuário pedir para "ativar o harness do smartfox", "smartfox", "elaborar questões no AvaliA", "banco de questões AvaliA", "SmartFox Autônomo" ou executar automações e diagnósticos no AvaliA Grupo A.
---

# Skill: Automação e Ferramentas com SmartFox Autônomo 11.2

Esta skill orienta a execução, operação e diagnóstico do **SmartFox Autônomo 11.2** integrado ao **AvaliA Grupo A** (`avalia.grupoa.com.br`).

---

## 1. Gatilhos de Ativação
Esta skill deve ser ativada sempre que o usuário mencionar:
- *"ativar o harness do smartfox"* / *"harness smartfox"*
- *"smartfox"* / *"smart fox"*
- *"questões no avalia"* / *"banco de itens grupo a"*
- *"instalar smartfox no Linux"*

---

## 2. Localização do Projeto e Componentes
- **Diretório Raiz**: `/home/hamilcar/Antigravity/smartfox/`
- **Código da Extensão Chrome**: `/home/hamilcar/Antigravity/smartfox/src/extensao/`
- **Harness de Diagnóstico**: `/home/hamilcar/Antigravity/smartfox/harness/smartfox_harness.py`
- **Scripts de Execução e Instalação**: `/home/hamilcar/Antigravity/smartfox/scripts/`
  - `instalar_linux.sh`: Instala e vincula a extensão localmente.
  - `executar_chrome_smartfox.sh`: Abre o Google Chrome no AvaliA com a extensão ativa.
- **Documentação**: `/home/hamilcar/Antigravity/smartfox/docs/COMECE_AQUI.html`

---

## 3. Diretrizes de Operação
1. O SmartFox é desenhado especificamente para o **AvaliA** (`https://avalia.grupoa.com.br/*`).
2. Adiciona o ícone da raposa 🦊 na interface para acesso ao Hub de Ferramentas, Banco de Materiais, Leitura de Word/PDF e Correção Discursiva.
