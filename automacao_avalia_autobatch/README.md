# AVALIA AutoBatch — Automação de Questões no AVA (Grupo A)

Este harness gerencia a automação completa de envio e preenchimento de questões acadêmicas no portal AVA / AVALIA do Grupo A via Playwright e injeção/mutação direta no modelo DOM Vue.js, além de disponibilizar aplicativo desktop com interface gráfica (GUI).

---

## 📁 Estrutura do Harness

```
automacao_avalia_autobatch/
├── src/                         # Mecanismos de automação e scripts principais
│   ├── app_avalia_gui.py        # Interface Desktop para operador
│   ├── automate_questions.py    # Engine de automação Playwright CLI
│   ├── automate_questions_v3.py # Engine avançada
│   ├── auto_batch_runner.py     # Executor sequencial
│   └── master_question_runner.py
├── disciplinas/                 # Scripts específicos e geradores por disciplina
│   ├── submit_all_*.py          # Submissão direta das 22 disciplinas
│   ├── build_batch_*.py         # Construtores de batches ADS, PS e TG
│   ├── build_all_disciplines.py # Construtor mestre
│   └── generate_all_22_exams.py
├── planilhas/                   # Matrizes e planilhas de questões
│   ├── Planilha_AVALIA_AD_*     (xlsx, xls, csv)
│   ├── questoes_ad_*
│   └── Tabela_Arquivos_AD.xlsx
├── distribuicao/                # Empacotamento Windows e Instaladores
│   ├── AVALIA_AutoBatch.spec
│   ├── AVALIA_AutoBatch_Setup.iss
│   ├── build_windows_exe.py
│   └── pacotes zip/tar.gz
├── testes_inspecao/             # Scripts diagnósticos de DOM e navegadores
│   ├── open_avalia_browser.py
│   ├── inspect_dom.py, check_submit_btns.py, etc.
│   └── capturas de tela e html de depuração
└── docs/                        # Documentação e guias de uso
    ├── README_Instalador.md
    └── Roteiro_de_Uso_AVALIA_AutoBatch.md
```

---

## 🚀 Como Executar

### 1. Interface Gráfica (Desktop GUI)
```bash
cd /home/hamilcar/Antigravity
source venv/bin/activate
python3 automacao_avalia_autobatch/src/app_avalia_gui.py
```

### 2. Linha de Comando (CLI)
```bash
cd /home/hamilcar/Antigravity
source venv/bin/activate
python3 automacao_avalia_autobatch/src/automate_questions.py automacao_avalia_autobatch/planilhas/Planilha_AVALIA_AD_Exemplo.xlsx
```
