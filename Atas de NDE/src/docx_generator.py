import os
import subprocess
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

TEMPLATES_DIR = '/home/hamilcar/Antigravity/Atas de NDE/templates'
LOCAL_OUTPUT_DIR = '/home/hamilcar/Antigravity/Atas de NDE/atas_geradas'

BASE_URI_NDE = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1CCAfj2zR02OVB6ZK8aKDSswSWWgN9d0Z/14vK9cSmyiafTIP2ZAyO5UN-E2pK_3YCE/1Sg5W3wVrRdklSyDC9y_pmLw7mBTi8MrJ/1eJtpGliy4asC2UEeRRCp3nRqemlOJnLm'
BASE_URI_COL = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1CCAfj2zR02OVB6ZK8aKDSswSWWgN9d0Z/14vK9cSmyiafTIP2ZAyO5UN-E2pK_3YCE/1PSqk0Yv-s-zs7ZT6dtaSVnPDLFl5ivLR/1ar3N8zEEt8Tr1H7Jy4-zLu7rxplKrrjr'

MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

def format_date_extenso(data_str):
    parts = data_str.split('/')
    dia = int(parts[0])
    mes = int(parts[1])
    ano = parts[2]
    return f"{dia} de {MESES[mes]} de {ano}"

def set_cell_content(cell, text, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=10):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(font_size)
    run.bold = bold

def update_metadata_table(table, data_str, inicio_str, termino_str, periodo_str):
    set_cell_content(table.rows[0].cells[0], f'DATA: {data_str}', bold=True, font_size=10)
    set_cell_content(table.rows[0].cells[1], f'INÍCIO: {inicio_str}', bold=True, font_size=10)
    set_cell_content(table.rows[0].cells[2], f'TÉRMINO: {termino_str}', bold=True, font_size=10)
    set_cell_content(table.rows[0].cells[3], f'PERÍODO: {periodo_str}', bold=True, font_size=10)

def populate_content_table(table, rows_data):
    for idx, (c0, c1, c2) in enumerate(rows_data):
        row_idx = idx + 1
        row = table.rows[row_idx]
        is_bold_title = True
        set_cell_content(row.cells[0], c0, bold=is_bold_title, font_size=10)
        set_cell_content(row.cells[1], c1, bold=False, font_size=10)
        set_cell_content(row.cells[2], c2, bold=False, font_size=10)

def update_footer(doc, tipo, data_str, sigla="ADS"):
    data_ext = format_date_extenso(data_str)
    if tipo == "NDE":
        footer_text = f"Ata de Reunião NDE de {sigla} – {data_ext}"
    else:
        footer_text = f"Ata de Reunião de Colegiado de {sigla} – {data_ext}"
    
    for section in doc.sections:
        footer = section.footer
        if footer.paragraphs:
            p = footer.paragraphs[0]
            p.text = ''
        else:
            p = footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(footer_text)
        run.font.name = 'Arial'
        run.font.size = Pt(10)

def generate_nde_doc(data_str, inicio_str, termino_str, periodo_str, rows_data, output_path, sigla="ADS"):
    template_path = os.path.join(TEMPLATES_DIR, 'template_nde_base.docx')
    doc = docx.Document(template_path)
    
    # Table 1: Metadata
    update_metadata_table(doc.tables[1], data_str, inicio_str, termino_str, periodo_str)
    
    # Table 2: Content (Pautas)
    populate_content_table(doc.tables[2], rows_data)
    
    # Footer: Date and title matching metadata
    update_footer(doc, "NDE", data_str, sigla)
    
    doc.save(output_path)
    print(f"Salvo documento NDE: {output_path} (Rodapé: {data_str})")

def generate_colegiado_doc(data_str, inicio_str, termino_str, periodo_str, rows_data, output_path, sigla="ADS"):
    template_path = os.path.join(TEMPLATES_DIR, 'template_colegiado_base.docx')
    doc = docx.Document(template_path)
    
    # Table 1: Metadata
    update_metadata_table(doc.tables[1], data_str, inicio_str, termino_str, periodo_str)
    
    # Table 2: Content (Pautas)
    populate_content_table(doc.tables[2], rows_data)
    
    # Footer: Date and title matching metadata
    update_footer(doc, "Colegiado", data_str, sigla)
    
    doc.save(output_path)
    print(f"Salvo documento Colegiado: {output_path} (Rodapé: {data_str})")

def ensure_gdrive_folder(base_uri, folder_name):
    target_uri = f"{base_uri}/{folder_name}"
    check = subprocess.run(['gio', 'info', target_uri], capture_output=True, text=True)
    if check.returncode != 0:
        print(f"Criando subpasta {folder_name} em {base_uri}...")
        mk = subprocess.run(['gio', 'mkdir', target_uri], capture_output=True, text=True)
        if mk.returncode == 0:
            print(f"Subpasta {folder_name} criada com sucesso!")
        else:
            print(f"Erro ao criar subpasta: {mk.stderr}")
    else:
        print(f"Subpasta {folder_name} já existe em {base_uri}")
    return target_uri

def copy_to_gdrive(local_file, target_folder_uri):
    fname = os.path.basename(local_file)
    dest_uri = f"{target_folder_uri}/{fname}"
    print(f"Copiando {fname} para {target_folder_uri}...")
    cp = subprocess.run(['gio', 'copy', local_file, dest_uri], capture_output=True, text=True)
    if cp.returncode == 0:
        print(f"Sucesso: {fname} copiado para o Google Drive!")
    else:
        print(f"Erro ao copiar {fname}: {cp.stderr}")
