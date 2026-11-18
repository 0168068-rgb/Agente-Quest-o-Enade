import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Lista dos arquivos da imagem
file_list = [
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

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Lista de Arquivos AD"

# Formatting styles
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

headers = ["#", "Nome do Arquivo", "Disciplina / Assunto", "Status", "Observações"]
ws.append(headers)

# Apply header formatting
for col_num, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_num)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")

# Add data rows
for idx, name in enumerate(file_list, 1):
    # Extract subject name by stripping 'AD ' and '.docx'
    subject = name.replace("AD ", "").replace(".docx", "")
    row_data = [idx, name, subject, "Pendente", ""]
    ws.append(row_data)

# Styling data rows
for row in range(2, len(file_list) + 2):
    ws.cell(row=row, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=row, column=2).alignment = Alignment(horizontal="left", vertical="center")
    ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", vertical="center")
    ws.cell(row=row, column=4).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=row, column=5).alignment = Alignment(horizontal="left", vertical="center")
    
    for col in range(1, 6):
        ws.cell(row=row, column=col).border = thin_border

# Auto-adjust column widths
for col in ws.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

excel_path = "Tabela_Arquivos_AD.xlsx"
wb.save(excel_path)
print(f"Excel salvo com sucesso em {excel_path}")
