# Automação WhatsApp — Comunicação e Disparos para Alunos

Harness para automação de mensagens, boas-vindas a calouros, comunicados acadêmicos para turmas e gestão de grupos via WhatsApp Web e Evolution API.

---

## 📁 Estrutura do Harness

```
automacao_whatsapp_alunos/
├── src/
│   ├── disparar_mensagens_boas_vindas.py   # Disparo de boas-vindas
│   ├── disparar_via_whatsapp_web_oficial.py # Automação via navegador oficial
│   ├── enviar_agora_whatsapp_web.py        # Disparo imediato
│   ├── enviar_mensagens_alunos.py          # Envio baseado em listas
│   ├── adicionar_alunos_grupo.py           # Adição automática em grupos
│   ├── buscar_grupo.py                     # Localizador de grupos da disciplina
│   ├── auto_monitor_e_disparar.py          # Monitoramento contínuo
│   └── servidor_qrcode.py                  # Servidor local para autenticação QR Code
├── evolution_api/
│   └── evolution-whatsapp/                 # Módulo de integração via Evolution API
├── contatos/
│   ├── contatos_whatsapp.vcf
│   ├── contatos_whatsapp_limpos.xlsx / .csv
│   └── contatos_google.csv
├── relatorios/
│   ├── relatorio_envio_boas_vindas.json
│   └── relatorio_envio_whatsapp.json
└── web/
    ├── ver_qrcode.html                     # Visualizador de autenticação
    └── qr_code_whatsapp.png
```

---

## 🚀 Como Executar

### 1. Iniciar Servidor de QR Code
```bash
python3 automacao_whatsapp_alunos/src/servidor_qrcode.py
```

### 2. Disparar Mensagens de Boas-Vindas
```bash
python3 automacao_whatsapp_alunos/src/disparar_mensagens_boas_vindas.py
```
