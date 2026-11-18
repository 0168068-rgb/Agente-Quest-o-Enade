---
name: smartduck
description: Use esta skill sempre que o usuário pedir para "ativar o harness do smartduck", "smartduck", "lançar notas no SophiA", "conferir notas AVA e SophiA" ou executar diagnósticos e automações com o SmartDuck 1.9.0.
---

# Skill: Automação e Auditoria com SmartDuck 1.9.0

Esta skill orienta a execução, manutenção e operação do **Harness do SmartDuck 1.9.0** para conciliação e lançamento de notas acadêmicas entre o **Portal SophiA Docente** e o **AVA Uni Grupo A**.

---

## 1. Gatilhos de Ativação
Esta skill deve ser ativada sempre que o usuário mencionar:
- *"ativar o harness do smartduck"* / *"harness smartduck"*
- *"smartduck"*
- *"lançamento de notas SophiA"*
- *"conferência AVA e SophiA"*
- *"instalar smartduck no Linux"*

---

## 2. Localização do Projeto e Componentes
- **Diretório Raiz**: `/home/hamilcar/Antigravity/smartduck/`
- **Código da Extensão Chrome**: `/home/hamilcar/Antigravity/smartduck/src/extensao/`
- **Harness & Guardrails**: `/home/hamilcar/Antigravity/smartduck/harness/smartduck_harness.py`
- **Scripts de Execução e Instalação**: `/home/hamilcar/Antigravity/smartduck/scripts/`
  - `instalar_linux.sh`: Instala e vincula a extensão localmente.
  - `executar_chrome_smartduck.sh`: Abre o Google Chrome já carregando a extensão sem intervenção manual.
- **Configuração**: `/home/hamilcar/Antigravity/smartduck/config/config_smartduck.json`

---

## 3. Diretrizes de Operação e Segurança
1. **Nunca sobrescrever notas existentes**: Por padrão, o SmartDuck atua apenas em campos vazios e editáveis (AD, AI, PS).
2. **Conferência antes do Lançamento**: Sempre preferir a opção de auditoria diagnóstica para validar divergências de alunos antes de gravar notas.
3. **Download de Relatório Excel**: Garantir a conferência da planilha `.xlsx` exportada ao término de cada lote.
