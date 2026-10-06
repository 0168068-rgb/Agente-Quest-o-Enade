---
name: gerador-questoes-enade
description: Use esta skill sempre que o usuário pedir para "ativar o harness do gerador ENADE", "gerador-questões-enade", fornecer um PDF de UA para criar questões, criar questões no padrão ENADE ou solicitar entregas em formato Word (.docx).
---

# Skill: Gerador de Questões no Padrão ENADE

Esta skill orienta a execução autônoma e interativa do **Harness do Agente Gerador de Questões ENADE** para os cursos de Análise e Desenvolvimento de Sistemas (ADS), Gestão da TI, Redes de Computadores e Ciência da Computação.

---

## 1. Gatilhos de Ativação
Esta skill deve ser ativada sempre que o usuário mencionar:
- *"ativar o harness do gerador ENADE"*
- *"gerador-questões-enade"* / *"gerador-questoes-enade"*
- *"gerar questão no padrão ENADE"*
- *"simulado ENADE"*
- *"questão ENADE em Word"* / *"questão ENADE em docx"*

---

## 2. Localização do Projeto e Harness
- **Diretório do Projeto**: `/home/hamilcar/Antigravity/agente_gerador_questoes_enade/`
- **Contexto Mestre**: `context/system_prompt_especialista_enade.md`
- **Exportador Word**: `src/docx_exporter.py`
- **Memória de Longo Prazo**: `memory/long_term/enade_knowledge_base.json` e `memory/long_term/padroes_distratores_inep.json`
- **Guardrails**: `guardrails/validator_enade.py` e `guardrails/bloom_depth_verifier.py`

---

## 3. Fluxo Principal: Diálogo Interativo (4 Passos)

Ao ativar o harness sem PDF, o agente conduz a interação pelos 4 passos:
- **Passo 1**: Seleção do Curso (ADS, GTI, Redes, Ciência da Computação, Formação Geral).
- **Passo 2**: Definição do Tópico Técnico.
- **Passo 3**: Seleção do Tipo Estrutural (1 - Escolha Combinada `I, II, III`, 2 - Múltipla Escolha Direta, 3 - Asserção-Razão `PORQUE`, 4 - Discursiva).
- **Passo 4**: Execução com Guardrails e Entregável Bifurcado em Markdown e Word (.docx).

---

## 4. Fluxo Alternativo: Geração a partir de Arquivo PDF (Unidade de Aprendizagem - UA)

Se o usuário fornecer o caminho de um arquivo PDF (ex: `/home/hamilcar/OneDrive/.../*.pdf`):
1. **Leitura e Extração de Objetivos**: Ler o PDF e extrair os **Objetivos de Aprendizagem** oficiais da abertura do capítulo.
2. **Apresentação de Objetivos**: Exibir os objetivos extraídos e permitir que o usuário escolha mapeá-los para os tipos estruturais.
3. **Geração Bifurcada em Word (.docx)**: Executar a geração garantindo a entrega da **Parte I (Estudante)** limpa e **Parte II (Professor)** completa com a Ficha de 23 campos e justificativas A a E, gerando o arquivo `.docx`.

---

## 5. Estrutura do Entregável Bifurcado Obrigatório

1. **PARTE I — Versão do Estudante (Limpa)**:
   - Contexto realista, recurso gráfico/código, comando (Bloom Nível 2/3/4) e Alternativas A a E. **Sem gabarito ou sinalização visual da resposta.**

2. **PARTE II — Versão do Professor (Completa)**:
   - **Ficha de Especificação de 23 Campos** preenchida.
   - **Gabarito Oficial e Resolução Comentada Passo a Passo**.
   - **Justificativa Individual de cada distrator (A, B, C, D, E)** ou **Rubrica Analítica de Correção Fracionada**.

---

## 6. Formato de Arquivo Obrigatório (.docx / Microsoft Word)
- **Regra de Exportação Permanente**: Toda questão gerada DEVE ser disponibilizada e salva no formato **Microsoft Word (`.docx`)** através do exportador `docx_exporter.py` do projeto.
- O arquivo `.docx` gerado mantém a estrutura bifurcada (Versão do Estudante e Versão do Professor com Ficha e Justificativas), pronto para impressão imediata ou edição pelo professor.
