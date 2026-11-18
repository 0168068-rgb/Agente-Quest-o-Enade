# Integração Google Workspace — Drive, Gmail, Calendar e Meet

Harness central de autenticação OAuth 2.0 e automação de serviços do ecossistema Google Workspace.

---

## 📁 Estrutura do Harness

```
integracao_google_workspace/
├── src/
│   ├── autenticar_google.py       # Fluxo OAuth e renovação de tokens
│   ├── login_google.py            # Autenticação de sessão
│   ├── calendar_manager.py        # Gestão de eventos no Google Calendar
│   ├── gmail_manager.py           # Envio e leitura de e-mails via API Gmail
│   ├── listar_drive.py            # Consulta a diretórios no Google Drive
│   ├── enviar_drive.py            # Upload de arquivos para pastas remotas
│   ├── enviar_ai_drive.py         # Upload de avaliações institucionais
│   ├── enviar_ps_drive.py         # Upload de provas substitutivas
│   ├── executar_copia_drive.py    # Backup e replicação em nuvem
│   ├── send_simulado_reports.py   # Envio de relatórios aos alunos
│   └── automate_meet_form.py      # Automação de formulários de reuniões Meet
├── credenciais_tokens/
│   ├── credentials_gmail.json     # Chaves de API Google Cloud
│   ├── token_calendar.json        # Tokens de acesso (escopos específicos)
│   ├── token_drive.json
│   ├── token_drive_rw.json
│   ├── token_gmail.json
│   └── check_google_session.py    # Verificação de validade de sessão
└── diagnostico_planilhas/
    ├── inspecionar_planilhas.py   # Inspeção e mapeamento de IDs de planilhas
    ├── inspecionar_vinculos.py
    └── atualizar_todas_planilhas_segunda_entrada.py
```

---

## 🚀 Como Executar

### 1. Autenticar ou Renovar Credenciais Google
```bash
python3 integracao_google_workspace/src/autenticar_google.py
```

### 2. Testar Listagem de Pastas no Drive
```bash
python3 integracao_google_workspace/src/listar_drive.py
```
