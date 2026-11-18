# Automação Sophia — Lançamento de Frequência e Notas

Harness especializado na automação de tarefas acadêmicas no sistema Sophia (lançamento de faltas, presenças e notas de avaliações a partir de planilhas Excel/Google Sheets).

---

## 📁 Estrutura do Harness

```
automacao_sophia_frequencia_notas/
├── src/
│   ├── app_frequencia_sophia.py         # Aplicativo Desktop com interface gráfica
│   ├── registrar_frequencia_sophia.py   # Automação de faltas e presenças
│   └── registrar_notas_sophia.py        # Automação de notas N1/N2/Sub/Exame
├── config/
│   ├── config_usuario.json              # Configurações de login e perfil
│   ├── LancadorFrequenciaSophia.spec    # Especificação PyInstaller
│   └── compilar_windows.bat             # Script de build para executável Windows
├── modelos_planilhas/
│   ├── Controle_de_presenca_Python.xlsx # Modelo de planilha de presenças
│   ├── Modelo_Planilha_Notas_Exemplo.xlsx # Modelo de notas
│   └── relatorio_lancamento_notas.xlsx  # Relatório gerado pós-lançamento
├── pacote_tia_andrea/                   # Pacote standalone para a Profa. Andrea
│   └── Tia andrea/
└── testes_debug/                        # Scripts e capturas de depuração de tela
    ├── scratch/
    └── scratch_Professor.*, professor_live.*
```

---

## 🚀 Como Executar

### 1. Lançador com Interface Gráfica (GUI)
```bash
cd /home/hamilcar/Antigravity
source venv/bin/activate
python3 automacao_sophia_frequencia_notas/src/app_frequencia_sophia.py
```

### 2. Lançador de Frequência Direto (CLI)
```bash
python3 automacao_sophia_frequencia_notas/src/registrar_frequencia_sophia.py
```

### 3. Lançador de Notas Direto (CLI)
```bash
python3 automacao_sophia_frequencia_notas/src/registrar_notas_sophia.py
```
