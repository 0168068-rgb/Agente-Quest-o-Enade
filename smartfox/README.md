# 🦊 SmartFox Autônomo 11.2 — Ferramentas do Professor no AvaliA

Extensão e suíte de ferramentas do professor integradas à plataforma **AvaliA Grupo A** (`avalia.grupoa.com.br`), adaptadas para operação autônoma no Linux dentro do ecossistema **Antigravity**.

---

## 📁 Estrutura do Diretório

```
smartfox/
├── config/
│   └── config_smartfox.json           # Configurações do ambiente
├── docs/
│   ├── COMECE_AQUI.html               # Guia visual do SmartFox
│   ├── EDICAO_AUTONOMA.txt            # Notas de versão da edição autônoma
│   ├── VALIDACAO.txt                  # Relatório de testes e integridade
│   └── avisos-originais/              # Licenças e políticas
├── harness/
│   ├── context/
│   │   └── system_prompt_smartfox.md  # Instruções de contexto para o agente
│   ├── fixtures/                      # Dados de teste
│   ├── guardrails/                    # Validadores
│   ├── relatorios/                    # Exportações geradas
│   └── smartfox_harness.py            # Script principal de teste do harness
├── pacotes/
│   └── SmartFox_Autonomo_11.2.zip     # Arquivo original preservado
├── scripts/
│   ├── instalar_linux.sh              # Script instalador nativo para Linux
│   └── executar_chrome_smartfox.sh    # Lançador do Chrome no AvaliA
├── src/
│   ├── extensao/                      # Código-fonte da extensão (Manifest V3)
│   └── arquivos_originais/            # Scripts e arquivos do pacote Windows original
├── tests/                             # Suíte de testes
└── README.md                          # Documentação de arquitetura e uso
```

---

## 🚀 Como Carregar no Chrome

1. Abra a aba de extensões: `chrome://extensions`
2. Ative o **Modo do desenvolvedor** (canto superior direito).
3. Clique em **Carregar sem compactação**.
4. Selecione a pasta:
   ```
   /home/hamilcar/Antigravity/smartfox/src/extensao
   ```
   *(ou `~/.local/share/smartfox/extensao`)*
5. Volte para a aba do **AvaliA** (`avalia.grupoa.com.br`) e pressione **F5** (Recarregar).
6. O ícone da raposa 🦊 e o menu de ferramentas aparecerão integrados na interface do AvaliA!
