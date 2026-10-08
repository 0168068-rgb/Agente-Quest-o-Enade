import os
import sys

base_dir = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD"

# Os 22 nomes dos arquivos da lista do usuário
docx_files = [
    "AD Cabeamento estruturado II.docx",
    "AD Compiladores.docx",
    "AD Desenvolvimento de Dispositivos Móveis.docx",
    "AD Estrutura de Dados.docx",
    "AD Gerenciamento de redes de computadores.docx",
    "AD Infraestrutura de redes.docx",
    "AD Infraestrutura de TI.docx",
    "AD Infraestrutura e serviços de TI.docx",
    "AD Interação Humano-Computador.docx",
    "AD Programação em PYTHON.docx",
    "AD Programação WEB II - Desenvolvimento back-end.docx",
    "AD Projeto de Redes de Computadores.docx",
    "AD Redes Convergentes.docx",
    "AD Redes de Alta Disponibilidade.docx",
    "AD Redes de Computadores.docx",
    "AD Redes de Longa Distância.docx",
    "AD Redes Sem Fio.docx",
    "AD Segurança da Informação e Legislação.docx",
    "AD Segurança da informação.docx",
    "AD Segurança de redes de computadores.docx",
    "AD Servidores e Computação na Nuvem.docx",
    "AD Sistemas Operacionais de Redes Abertas.docx"
]

print("Pesquisando estruturas de disciplinas em NEAD...")
sys.stdout.flush()

# 1. Mapear todas as pastas de disciplina e procurar subpastas de questões/AD
all_dirs = []
for entry in os.listdir(base_dir):
    full_p = os.path.join(base_dir, entry)
    if os.path.isdir(full_p):
        all_dirs.append(entry)

# Vamos procurar especificamente por arquivos .xlsx nas subpastas
found_files = {}

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.lower().endswith(('.xlsx', '.xls')):
            rel_p = os.path.relpath(os.path.join(root, f), base_dir)
            found_files[f.lower()] = (f, rel_p)

print(f"Total de planilhas Excel (.xlsx/.xls) encontradas na pasta NEAD: {len(found_files)}")
print("--------------------------------------------------")

for docx in docx_files:
    # Nome esperado sem extensão .docx (ex: "ad cabeamento estruturado ii.xlsx")
    base_name = docx[:-5].lower() # remove .docx
    expected_xlsx = base_name + ".xlsx"
    expected_xls = base_name + ".xls"
    
    # Checar se existe exato match ou parcial match
    exact_match = None
    if expected_xlsx in found_files:
        exact_match = found_files[expected_xlsx]
    elif expected_xls in found_files:
        exact_match = found_files[expected_xls]
    else:
        # Tentar busca parcial flexível
        for key, val in found_files.items():
            if base_name in key or key.replace(".xlsx","").replace(".xls","") in base_name:
                exact_match = val
                break
                
    if exact_match:
        print(f"✅ ENCONTRADO para [{docx}]:")
        print(f"   -> Arquivo: {exact_match[0]}")
        print(f"   -> Caminho: {exact_match[1]}")
    else:
        print(f"❌ FALTANDO Excel para [{docx}]")
        print(f"   -> Esperado: {docx[:-5]}.xlsx")

