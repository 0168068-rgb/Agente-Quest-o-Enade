# 🤖 Projeto Agente de IA para Geração de Questões no Padrão ENADE

Este projeto implementa a **estrutura de harness completa de um Agente de IA** especializado na criação, revisão e validação de questões inéditas no padrão **INEP / ENADE** para os cursos de **Análise e Desenvolvimento de Sistemas (ADS)**, **Gestão da TI**, **Redes de Computadores** e **Ciência da Computação**.

---

## 🏗️ Estrutura Harness Completa do Agente

O projeto segue a arquitetura moderna de agentes autônomos, dividida nos seguintes módulos:

```
agente_gerador_questoes_enade/
├── README.md                                  <- Documentação completa e guia de uso
├── requirements.txt                            <- Dependências do projeto Python
├── config/                                    <- Configurações do agente e regras
│   ├── agent_config.yaml                      <- Modelos, temperatura e hiperparâmetros
│   └── enade_rules.json                       <- Cursos, tipos e escopos permitidos
├── context/                                   <- Contexto e Prompts de Sistema
│   └── system_prompt_especialista_enade.md    <- Prompt especialista com fórmula e regras
├── memory/                                    <- Sistema de Memória do Agente
│   ├── short_term/                            <- Memória de Curto Prazo (Sessão Ativa)
│   │   └── session_store.json                 <- Estado da conversa/geração atual
│   └── long_term/                             <- Memória de Longo Prazo (Persistente)
│       ├── enade_knowledge_base.json          <- DCNs, Matrizes e Taxonomia de Bloom
│       ├── padroes_distratores_inep.json      <- Tipologia de erros comuns para distratores
│       └── banco_questoes_historico.json      <- Histórico de questões já geradas
├── guardrails/                                <- Motores de Validação e Segurança
│   ├── validator_enade.py                     <- Validador dos 18 pontos do checklist e 23 campos
│   ├── bloom_depth_verifier.py                <- Bloqueador de Nível 1 (memorização)
│   └── checklist_18_pontos.json               <- Matriz de verificação automatizada
├── templates/                                 <- Modelos e Esquemas Estruturados
│   ├── ficha_especificacao_23_campos.json     <- Esquema dos 23 campos obrigatórios
│   ├── versao_estudante_template.md           <- Template limpo sem gabarito
│   └── versao_professor_template.md           <- Template completo com resoluções
└── src/                                       <- Código-Fonte do Agente
    ├── __init__.py
    ├── memory_manager.py                      <- Carregamento e salvamento de memórias
    ├── guardrail_engine.py                    <- Execução de checagens pré/pós geração
    ├── agent_core.py                          <- Orquestrador principal do agente
    └── runner.py                             <- CLI Executor
```

---

## ⚡ Como Funciona a Conexão? (Resposta à Dúvida sobre Conexão)

### **Existe a necessidade de conexão com a Internet ou API Externa?**

Depende do modo de execução que você escolher:

1. **Modo 1: Com Conexão de API Externa (Google Gemini API / OpenAI / Antigravity SDK)** — *Recomendado para Geração Automática Total*
   - **Precisa de Conexão?** **SIM.**
   - **Como funciona**: O `agent_core.py` envia o prompt montado (com todo o contexto, memória e guardrails) para a API oficial dos modelos da Google (`google-genai` ou Gemini API) via internet, recebendo a questão pronta em segundos.
   - **Requisito**: Uma chave de API (`GEMINI_API_KEY`) configurada no seu ambiente.

2. **Modo 2: Modo Local / Offline (Servidor Local Ollama / Llama.cpp ou Execução Pair Programming via Antigravity)** — *Totalmente Offline*
   - **Precisa de Conexão?** **NÃO.**
   - **Como funciona**: Todo a estrutura de Harness (arquivos de contexto, memórias em JSON, templates e o validador Python em `guardrails/validator_enade.py`) roda **100% localmente no seu computador**. Se você usar um LLM local rodando via Ollama/vLLM ou continuar trabalhando diretamente comigo (seu assistente local Antigravity), **nenhuma conexão externa é necessária**.

---

## 🚀 Como Executar o Agente

### 1. Testar a montagem do agente via linha de comando:
```bash
python3 src/runner.py --curso ADS --topico "Arquitetura de Microsserviços e Circuit Breaker" --tipo ESCOLHA_COMBINADA
```

### 2. Testar o motor de Guardrails:
```python
from guardrails.validator_enade import ENADEValidator

validador = ENADEValidator()
resultado = validador.validate_bifurcation(texto_markdown)
print(resultado)
```

---

## 🎯 Garantias de Qualidade Incorporadas no Harness
- **Fórmula de Habilidade Observável**: `Habilidade + Conhecimento + Situação/Restrições + Raciocínio + Evidência`.
- **Bloqueio de Nível 1 de Bloom**: O `bloom_depth_verifier.py` impede a criação de questões de memorização pura.
- **Entregável Bifurcado Automático**: Garante a separação estrita da Versão do Estudante (limpa) e da Versão do Professor (com a Ficha de 23 campos e justificativas A a E).
