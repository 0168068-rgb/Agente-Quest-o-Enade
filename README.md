# Antigravity — Ecossistema de Automações e Habilidades

Repositório central de ferramentas, automações e harnesses operacionais acadêmicos. Cada projeto possui seu próprio harness isolado contendo código-fonte (`src`), configurações (`config`), modelos/dados e documentação.

---

## 🏗️ Estrutura Geral dos Harnesses

```
Antigravity/
├── Atas de NDE/                        # Geração de Atas de NDE e Colegiado (Modelos 2026)
├── agente_gerador_questoes_enade/       # Elaboração de Questões no Padrão ENADE / Kuestion
├── automacao_avalia_autobatch/         # Automação de Questões no AVA (Playwright / Vue.js / GUI)
├── automacao_sophia_frequencia_notas/  # Automação de Frequência e Notas no Sophia
├── automacao_whatsapp_alunos/          # Comunicação e Disparo de Mensagens via WhatsApp
└── integracao_google_workspace/        # Conexão OAuth com Drive, Gmail, Calendar e Meet
```

---

## 🛠️ Detalhamento dos Módulos

| Harness | Descrição | Tecnologias Principais |
| :--- | :--- | :--- |
| [**Atas de NDE**](./Atas%20de%20NDE/README.md) | Geração de atas institucionais com papel timbrado oficial 2026 em Word e PDF. | Python, `python-docx`, LibreOffice |
| [**Agente ENADE**](./agente_gerador_questoes_enade/README.md) | Especialista em elaboração de itens de avaliação ENADE com guardrails pedagógicos. | Python, Bloom Taxonomy, Kuestion |
| [**AVALIA AutoBatch**](./automacao_avalia_autobatch/README.md) | Preenchimento em lote de avaliações no AVA / Grupo A com interface Desktop. | Playwright, Python, Vue.js DOM |
| [**Automação Sophia**](./automacao_sophia_frequencia_notas/README.md) | Lançamento automatizado de presenças, faltas e notas acadêmicas. | Python, Selenium/Playwright, Openpyxl |
| [**Automação WhatsApp**](./automacao_whatsapp_alunos/README.md) | Disparos de boas-vindas e avisos acadêmicos para turmas e grupos. | Python, WhatsApp Web, Evolution API |
| [**Google Workspace**](./integracao_google_workspace/README.md) | Módulos de autenticação OAuth e gestão em nuvem (Drive, Gmail, Agenda). | Google APIs Client Library, OAuth 2.0 |

---

## 🧠 Habilidades e Regras Globais (.agents)

Todas as habilidades de desenvolvimento, segurança e automação estão disponíveis no diretório `.agents/skills/`:
- `ava-question-automation`: Instruções para o harness AVALIA AutoBatch.
- `gerador-atas-nde-colegiado`: Instruções para elaboração de atas institucionais.
- `gerador-questoes-enade` & `kuestion`: Instruções pedagógicas e fluxo interativo ENADE.
- `sincronizar-agente`: Sincronização entre múltiplos computadores via Git.
- Diversas habilidades técnicas de frontend, backend, testes e segurança.
