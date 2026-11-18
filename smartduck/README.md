# 🦆 SmartDuck 1.9.0 — Automação de Lançamento de Notas (SophiA & AVA)

Projeto de automação e conferência de notas acadêmicas entre o **Portal SophiA Docente** (`portal.sophia.com.br`) e o **AVA Uni Grupo A** (`avauni.grupoa.education`), adaptado para operação nativa no Linux dentro do ecossistema **Antigravity**.

---

## 📁 Estrutura do Diretório

```
smartduck/
├── config/
│   └── config_smartduck.json          # Parâmetros e endpoints de configuração
├── docs/
│   ├── COMECE-AQUI.txt                # Instruções operacionais originais
│   ├── LEIA-ME-INSTALACAO.html        # Guia visual de instalação
│   └── SHA256-1.9.0.txt               # Assinaturas e hashes de integridade
├── harness/
│   ├── context/
│   │   └── system_prompt_smartduck.md # Contexto mestre e instruções do agente
│   ├── fixtures/                      # Dados simulados para testes
│   ├── guardrails/
│   │   └── regras_validacao_smartduck.py # Validadores de notas, RA e integridade
│   ├── planilhas_entrada/             # Pasta de trabalho para arquivos de notas
│   ├── relatorios/                    # Exportações de relatórios Excel (.xlsx)
│   └── smartduck_harness.py           # Script principal de teste e diagnóstico do harness
├── pacotes/
│   └── SmartDuck_1.9.0_com_instalador.zip # Pacote original preservado
├── scripts/
│   ├── instalar_linux.sh              # Script instalador nativo para Linux
│   └── executar_chrome_smartduck.sh   # Lançador do Chrome com a extensão ativa
├── src/
│   ├── extensao/                      # Código-fonte completo da Extensão Chrome (Manifest V3)
│   └── instalador_windows/            # Fontes NSIS e executável Windows original
└── tests/                             # Suíte de testes de integração e unidade
```

---

## 🚀 Como Instalar e Usar no Linux

### Opção 1: Instalação Padrão no Perfil do Chrome
1. Execute o script instalador:
   ```bash
   bash scripts/instalar_linux.sh
   ```
2. Abra o Google Chrome e acesse:
   ```
   chrome://extensions
   ```
3. Ative o **Modo do desenvolvedor** (canto superior direito).
4. Clique em **Carregar sem compactação** (Load unpacked).
5. Selecione a pasta:
   ```
   ~/.local/share/smartduck/extensao
   ```
   *(ou diretamente `/home/hamilcar/Antigravity/smartduck/src/extensao`)*

### Opção 2: Execução Direta / Sessão Rápida
Se desejar abrir o Chrome já com a extensão carregada automaticamente para teste:
```bash
bash scripts/executar_chrome_smartduck.sh
```

---

## 🛡️ Execução do Harness Antigravity
Para validar a integridade da extensão, testar os guardrails de negócio e verificar a saúde dos módulos:
```bash
python3 harness/smartduck_harness.py
```

---

## 📌 Funcionalidades Principais
- **Conferência por Professor:** Valida vínculos docentes e participantes de turmas no AVA.
- **Lançamento em Lote:** Preenchimento automático e seguro de notas AD, AI e PS no SophiA.
- **Relatório Excel (.xlsx):** Gera relatórios detalhados com as abas:
  - *Turmas com divergências*
  - *Alunos só no AVA*
  - *Campos AD AI PS*
- **Proteção de Dados:** Preenchimento exclusivo de campos vazios/editáveis; confirmação obrigatória de gravação; sem injeção de fórmulas arbitrárias.
