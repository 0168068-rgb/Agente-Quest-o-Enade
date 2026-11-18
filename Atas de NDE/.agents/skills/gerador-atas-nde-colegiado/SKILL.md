---
name: gerador-atas-nde-colegiado
description: Gera atas formais de NDE e Colegiado de Curso para Instituições de Ensino Superior (EAD/Presencial), analisando histórico prévio no Google Drive ou local, gerenciando comissões docentes e exportando diretamente em Word (.docx e .pdf) no papel timbrado oficial.
---

# Skill: Gerador de Atas de NDE e Colegiado de Curso (Padrão Oficial 2026)

Esta skill orienta a produção de **Atas de Reunião do Núcleo Docente Estruturante (NDE)** e do **Colegiado de Curso** para cursos de Ensino Superior da UNIG / NEAD, adotando rigorosamente os **modelos oficiais institucionais de 2026**.

---

## 1. Gatilhos de Ativação
- *"gerar ata de nde"*
- *"ata nde"*
- *"ata colegiado"*
- *"gerar atas de nde e colegiado"*
- *"nova ata"*
- *"preencher atas faltantes"*

---

## 2. Modelos Oficiais Obrigatórios (Padrão 2026)
> [!CRITICAL]
> **REGRA FIXA**: De agora em diante, o assistente **SEMPRE** utilizará os modelos oficiais consolidados em `templates/`:

1. **Modelo Oficial NDE**:
   - Arquivo Base: `templates/template_nde_oficial_2026.docx` (originado de `ATA de NDE 15 JUl 2026.docx`)
   - Cabeçalho: Timbrado institucional oficial UNIG / NEAD.
   - Corpo: Inicia **diretamente na Tabela de 3 Colunas** (`Pauta / Assunto` | `Encaminhamento / Discussão` | `Sugestão`).
   - Linha 1: `ABERTURA` com data e horário por extenso e citação ao Presidente e membros.
   - Linhas 2 a 5: Pautas intermediárias (4 pautas acadêmicas densas com alternância de falas dos 5 docentes).
   - Linha 6: `ENCERRAMENTO`.
   - Tabela de Assinaturas: 5 membros nominais (Hamilcar Pereira da Silva, Alan Jefferson de Oliveira da Silva, Telmo Viana Rodrigues, Luciano Roberto Padilha de Andrade, Ronaldo Paulucci de Assis).

2. **Modelo Oficial Colegiado**:
   - Arquivo Base: `templates/template_colegiado_oficial_2026.docx` (originado de `COLEGIADO - TIMBRADO - MODELO.docx`)
   - Cabeçalho: Timbrado institucional oficial UNIG / NEAD.
   - Corpo: Inicia **diretamente na Tabela de 3 Colunas** (`Pauta e Assunto` | `Discussão` | `Aprovação`).
   - Linha 1: `Abertura` formal colegiada.
   - Linhas 2 a 5: Pautas deliberadas (`APROVADO por unanimidade`).
   - Linha 6: `Encerramento`.
   - Tabela de Assinaturas: 5 membros nominais (Hamilcar Pereira da Silva, Marcos Cruz De Azevedo, Selma Sant'Anna de Fonseca, Denise Moraes do Nascimento Vieira, Ana Carolina Ramos da Cruz).

3. **Rodapé Oficial**:
   - Numeração de páginas dinâmica (`PAGE`). Não inserir textos ou datas fixas no rodapé para evitar discrepâncias.

4. **Entregáveis**:
   - Geração pareada de `.docx` e conversão automática para `.docx.pdf` via LibreOffice.

---

## 3. Estrutura de Repositórios no Google Drive (GVFS)
O sistema lê e grava diretamente nos repositórios institucionais do Google Drive:
- **Pasta Raiz Institucional do MEC (`.ATAS`)**:
  `google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1OVWk6s2LEwXOp_jAQNacFZtVBSrS9r8i/1wm6ptLxn07qiNjEBWbSB4wvBcmw9jYsw/1bH60AUfQaf_bOCoE_EEWbSSP8BQQKyB3/1VLYMikZEF7_uiwgKsY9-Rf7sqBwAjg9b/1iOJbK7ie2eTkd71AfkpFz5tvSULG0u2d`
  - **NDE**: Subpasta `10FYLdH8hiyGs8hS0iT7boyGirQyMv2oD/1sQZsZ3cbGfewOWFG9cg2jh4OOm4zioI-` (`Atas/`) com pastas semestrais `23.1`, `23.2`, ..., `26.1`, `26.2`.
  - **Colegiado**: Subpasta `1oRyFokCNL7juuFi4eod5d64svfqf2LOg` (`Colegiado/`) com pastas semestrais `23.1`, `23.2`, ..., `26.1`, `26.2`.
- **Regra de Semestres**: Cada pasta semestral deve conter exatamente **duas atas** (uma de início e uma de encerramento de semestre).
