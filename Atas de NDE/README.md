# Gerador de Atas de NDE e Colegiado de Curso (Padrão Oficial 2026)

Harness oficial para elaboração, formatação e geração automatizada de atas de reunião do **Núcleo Docente Estruturante (NDE)** e do **Colegiado de Curso** para a UNIG / NEAD, em conformidade estrita com as portarias, mandatos e modelos institucionais de 2026.

---

## 📁 Estrutura do Harness

```
Atas de NDE/
├── src/                          # Motor de processamento e exportação
│   ├── docx_generator.py         # Preenchimento dinâmico dos modelos docx
│   ├── generate_redes_atas.py    # Gerador de atas do curso de Redes
│   ├── generate_gti_atas.py      # Gerador de atas do curso de GTI
│   ├── generate_new_model_atas.py # Gerador modelo novo consolidado
│   └── generate_all_missing_atas.py # Automação em lote de atas faltantes
├── config/                       # Parâmetros institucionais e docentes
│   ├── colegiado_redes.json      # Composição docente, mandatos e portarias
│   ├── nde_redes.json
│   ├── nde_gti.json
│   └── nde_ads.json
├── templates/                    # Modelos oficiais timbrados 2026 (.docx)
│   ├── modelo_ata_nde_2026.docx
│   └── modelo_ata_colegiado_2026.docx
├── atas_geradas/                 # Repositório de atas geradas (.docx e .pdf)
│   ├── atas_geradas_redes/
│   ├── atas_geradas_gti/
│   └── atas_geradas_modelo_novo/
└── historico/                    # Atas e minutas anteriores
    ├── ata_NDE(1º).md
    ├── Ata_Colegiado(2º).md
    └── atas de redes/
```

---

## 🚀 Como Executar

Através da skill do agente:
```
"gerar ata de nde"
"gerar ata colegiado"
```

Ou diretamente via Python:
```bash
python3 "Atas de NDE/src/generate_redes_atas.py"
```
