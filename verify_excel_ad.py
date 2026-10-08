import os
import glob

base_dir = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD"

# Os 22 arquivos .docx listados anteriormente
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

print("=== VERIFICAÇÃO DE ESTRUTURA DE PASTAS E ARQUIVOS EXCEL ===")

# Vamos varrer todo o diretório NEAD procurando por pastas de disciplinas e subpastas 'AD' ou arquivos Excel
results = []

for docx_name in docx_files:
    base_name = docx_name.replace(".docx", "") # Ex: "AD Cabeamento estruturado II"
    subject_clean = base_name.replace("AD ", "").strip()
    
    # Procurar arquivos excel (.xlsx, .xls, .csv) que contenham partes do nome da disciplina ou AD
    found_excel = []
    found_ad_folders = []
    
    # Busca por subpastas em NEAD
    for root, dirs, files in os.walk(base_dir):
        # Verificar se o caminho contém 'AD' ou 'questões' ou similares
        for f in files:
            if f.endswith(('.xlsx', '.xls', '.csv')):
                # Verificar se o nome bate com o arquivo esperado ou está dentro de uma pasta AD
                f_path = os.path.join(root, f)
                rel_path = os.path.relpath(f_path, base_dir)
                
                # Checar correspondência de nome
                f_no_ext = os.path.splitext(f)[0]
                if base_name.lower() in f_no_ext.lower() or subject_clean.lower() in f_no_ext.lower():
                    found_excel.append(rel_path)

    results.append({
        "docx": docx_name,
        "subject": subject_clean,
        "found_excel": found_excel
    })

for item in results:
    print(f"\n📄 Word: {item['docx']}")
    if item['found_excel']:
        print("  ✅ Excel encontrado(s):")
        for ex in item['found_excel']:
            print(f"     - {ex}")
    else:
        print("  ❌ NENHUM EXCEL ENCONTRADO!")
