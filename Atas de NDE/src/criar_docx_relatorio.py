import os
import shutil
import subprocess
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

OUTPUT_DOCX = '/home/hamilcar/Antigravity/Atas de NDE/Relatorio_Notas_Fisioterapia_AD_2026.2.docx'
DOWNLOADS_DOCX = '/home/hamilcar/Downloads/Relatorio_Notas_Fisioterapia_AD_2026.2.docx'

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=40, bottom=40, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D9DE", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def format_cell(cell, text, bold=False, italic=False, color_rgb=(0,0,0), align=WD_ALIGN_PARAGRAPH.LEFT, font_size=8.5, bg_color=None):
    if bg_color:
        set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=35, bottom=35, left=90, right=90)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(0.5)
    p.paragraph_format.space_after = Pt(0.5)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(str(text))
    run.font.name = 'Calibri'
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def generate_report():
    doc = docx.Document()

    # Formato A4 (210 x 297 mm)
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
        # Rodapé elegante
        footer = section.footer
        p_ft = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("Relatório de Alterações de Notas – Curso de Fisioterapia | Avaliação Diagnóstica 2026.2")
        r_ft.font.name = 'Calibri'
        r_ft.font.size = Pt(8)
        r_ft.font.color.rgb = RGBColor(120, 120, 120)

    # TÍTULO PRINCIPAL
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(1)
    r_tit = title_p.add_run("Relatório de Alterações de Notas – Avaliação Diagnóstica (AD)")
    r_tit.font.name = 'Calibri'
    r_tit.font.size = Pt(14)
    r_tit.bold = True
    r_tit.font.color.rgb = RGBColor(31, 73, 125)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(6)
    r_sub = sub_p.add_run("Curso de Fisioterapia – Semestre Letivo 2026.2 (3ª Entrada) | Emissão: 04 de novembro de 2026")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(9)
    r_sub.font.color.rgb = RGBColor(90, 90, 90)

    # QUADRO DE OBSERVAÇÃO INICIAL (Callout Box)
    callout_table = doc.add_table(rows=1, cols=1)
    callout_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    callout_cell = callout_table.cell(0, 0)
    set_cell_background(callout_cell, "F0F4F8")
    set_cell_margins(callout_cell, top=70, bottom=70, left=120, right=120)
    
    # Borda esquerda grossa e azul
    tcPr = callout_cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="1F497D"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(tcBorders)

    callout_p1 = callout_cell.paragraphs[0]
    callout_p1.paragraph_format.space_before = Pt(0)
    callout_p1.paragraph_format.space_after = Pt(2)
    r_c_tit = callout_p1.add_run("Observação Inicial:")
    r_c_tit.bold = True
    r_c_tit.font.name = 'Calibri'
    r_c_tit.font.size = Pt(9)
    r_c_tit.font.color.rgb = RGBColor(31, 73, 125)

    callout_p2 = callout_cell.add_paragraph()
    callout_p2.paragraph_format.space_before = Pt(0)
    callout_p2.paragraph_format.space_after = Pt(2)
    callout_p2.paragraph_format.line_spacing = 1.1
    r_c_txt1 = callout_p2.add_run(
        "Ao analisar os dados da Avaliação Diagnóstica (AD) para o curso de Fisioterapia, cabe uma observação inicial sobre os arquivos enviados:"
    )
    r_c_txt1.font.name = 'Calibri'
    r_c_txt1.font.size = Pt(8.5)

    callout_p3 = callout_cell.add_paragraph()
    callout_p3.paragraph_format.space_before = Pt(0)
    callout_p3.paragraph_format.space_after = Pt(1.5)
    callout_p3.paragraph_format.line_spacing = 1.1
    r_b1 = callout_p3.add_run("• Os dois arquivos anexados diretamente nesta sessão (")
    r_b1.font.name = 'Calibri'; r_b1.font.size = Pt(8.5)
    r_f1 = callout_p3.add_run("ad_ead_notas 2026.2.3.xlsx")
    r_f1.font.name = 'Calibri'; r_f1.font.size = Pt(8.5); r_f1.italic = True
    r_b2 = callout_p3.add_run(" e ")
    r_b2.font.name = 'Calibri'; r_b2.font.size = Pt(8.5)
    r_f2 = callout_p3.add_run("ad_ead_notas 333333.xlsx")
    r_f2.font.name = 'Calibri'; r_f2.font.size = Pt(8.5); r_f2.italic = True
    r_b3 = callout_p3.add_run(") possuem ")
    r_b3.font.name = 'Calibri'; r_b3.font.size = Pt(8.5)
    r_b4 = callout_p3.add_run("dados de notas idênticos.")
    r_b4.font.name = 'Calibri'; r_b4.font.size = Pt(8.5); r_b4.bold = True

    callout_p4 = callout_cell.add_paragraph()
    callout_p4.paragraph_format.space_before = Pt(0)
    callout_p4.paragraph_format.space_after = Pt(0)
    callout_p4.paragraph_format.line_spacing = 1.1
    r_b5 = callout_p4.add_run("• Contudo, ao comparar a base histórica anterior (")
    r_b5.font.name = 'Calibri'; r_b5.font.size = Pt(8.5)
    r_f3 = callout_p4.add_run("Notas de AD - EAD - 3ª Entrada.xlsx")
    r_f3.font.name = 'Calibri'; r_f3.font.size = Pt(8.5); r_f3.italic = True
    r_b6 = callout_p4.add_run(") com a base consolidada/atualizada (")
    r_b6.font.name = 'Calibri'; r_b6.font.size = Pt(8.5)
    r_f4 = callout_p4.add_run("ad_ead_notas 2026.2.3.xlsx")
    r_f4.font.name = 'Calibri'; r_f4.font.size = Pt(8.5); r_f4.italic = True
    r_b7 = callout_p4.add_run("), foram identificadas ")
    r_b7.font.name = 'Calibri'; r_b7.font.size = Pt(8.5)
    r_b8 = callout_p4.add_run("42 alterações de notas")
    r_b8.font.name = 'Calibri'; r_b8.font.size = Pt(8.5); r_b8.bold = True
    r_b9 = callout_p4.add_run(", englobando ")
    r_b9.font.name = 'Calibri'; r_b9.font.size = Pt(8.5)
    r_b10 = callout_p4.add_run("23 alunos distintos em 4 disciplinas")
    r_b10.font.name = 'Calibri'; r_b10.font.size = Pt(8.5); r_b10.bold = True
    r_b11 = callout_p4.add_run(" (todas com majoração de notas decorrente de recursos/anulações).")
    r_b11.font.name = 'Calibri'; r_b11.font.size = Pt(8.5)

    # SEÇÃO 1: RESUMO DAS ALTERAÇÕES POR DISCIPLINA
    h_sec1 = doc.add_paragraph()
    h_sec1.paragraph_format.space_before = Pt(8)
    h_sec1.paragraph_format.space_after = Pt(2)
    h_sec1.paragraph_format.keep_with_next = True
    r_s1 = h_sec1.add_run("Resumo das Alterações por Disciplina")
    r_s1.font.name = 'Calibri'; r_s1.font.size = Pt(11); r_s1.bold = True; r_s1.font.color.rgb = RGBColor(31, 73, 125)

    tbl_res = doc.add_table(rows=1, cols=5)
    tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_res, color="B8C7D9", sz="4")

    headers_res = ["Disciplina", "Código", "Período", "Qtd. Alunos Afetados", "Padrão da Mudança"]
    col_w_res = [Inches(2.7), Inches(0.8), Inches(0.8), Inches(1.1), Inches(1.8)]

    # Cabeçalho da tabela
    hdr_row = tbl_res.rows[0]
    hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for c_idx, h_text in enumerate(headers_res):
        cell = hdr_row.cells[c_idx]
        cell.width = col_w_res[c_idx]
        align = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
        format_cell(cell, h_text, bold=True, color_rgb=(255,255,255), align=align, font_size=8.5, bg_color="1F497D")

    linhas_resumo = [
        ("Fisioterapia Ortopédica e Tramatológica", "1313", "6º", "13", "50 ➔ 100 (+50) / 40 ➔ 80 (+40)"),
        ("Fisioterapia em Clínica Médica e Cirúrgica", "4062", "8º", "10", "70 ➔ 100 (+30) / 50 ➔ 72 (+22)"),
        ("Fisioterapia Dermatofuncional", "4063", "8º", "10", "70 ➔ 78 (+8) / 50 ➔ 56 (+6)"),
        ("Fisioterapia Cardiovascular", "4061", "8º", "9", "90 ➔ 100 (+10) / 80 ➔ 89 (+9)"),
    ]

    for idx, r_data in enumerate(linhas_resumo):
        row = tbl_res.add_row()
        row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        bg = "FFFFFF" if idx % 2 == 0 else "F7F9FB"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.width = col_w_res[c_idx]
            align = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            bold = True if c_idx in [0, 3] else False
            color = (31, 73, 125) if c_idx == 0 else (0, 0, 0)
            format_cell(cell, val, bold=bold, align=align, font_size=8, color_rgb=color, bg_color=bg)

    # Linha Total
    row_tot = tbl_res.add_row()
    row_tot._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for c_idx in range(5):
        row_tot.cells[c_idx].width = col_w_res[c_idx]
        set_cell_background(row_tot.cells[c_idx], "E9EFF5")
    format_cell(row_tot.cells[0], "Total", bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=8.5, bg_color="E9EFF5")
    format_cell(row_tot.cells[1], "-", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color="E9EFF5")
    format_cell(row_tot.cells[2], "-", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color="E9EFF5")
    format_cell(row_tot.cells[3], "42", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9, color_rgb=(31,73,125), bg_color="E9EFF5")
    format_cell(row_tot.cells[4], "4 disciplinas", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8, bg_color="E9EFF5")

    # SEÇÃO 2: DETALHAMENTO POR DISCIPLINA
    h_sec2 = doc.add_paragraph()
    h_sec2.paragraph_format.space_before = Pt(8)
    h_sec2.paragraph_format.space_after = Pt(2)
    h_sec2.paragraph_format.keep_with_next = True
    r_s2 = h_sec2.add_run("Detalhamento por Disciplina")
    r_s2.font.name = 'Calibri'; r_s2.font.size = Pt(11); r_s2.bold = True; r_s2.font.color.rgb = RGBColor(31, 73, 125)

    headers_det = ["RA", "Aluno(a)", "Polo", "Nota Anterior", "Nota Nova", "Variação"]
    col_w_det = [Inches(1.05), Inches(2.75), Inches(1.1), Inches(0.8), Inches(0.8), Inches(0.7)]

    disciplinas_det = [
        {
            "titulo": "1. Fisioterapia Ortopédica e Tramatológica (Cód. 1313) — 6º Período",
            "obs": "13 alterações registradas:",
            "alunos": [
                ("721002533", "Carla Cristina Garcia Portugal Nerys", "Nova Iguaçu", "50", "100", "+50"),
                ("721006618", "Daiana de França Luciano", "Nova Iguaçu", "50", "100", "+50"),
                ("721003315", "Emily de Almeida Flores", "Nova Iguaçu", "50", "100", "+50"),
                ("721003178", "Juliana de Carvalho da Silva", "Nova Iguaçu", "50", "100", "+50"),
                ("721006656", "Leticia Mello dos Santos Silva", "Nova Iguaçu", "50", "100", "+50"),
                ("721006721", "Marcos Eduardo da Silveira Jatobá", "Nova Iguaçu", "40", "80", "+40"),
                ("721006490", "Maria Eduarda Carmo Toledo", "Nova Iguaçu", "50", "100", "+50"),
                ("721006796", "Nathany Sanglard Tavares", "Nova Iguaçu", "50", "100", "+50"),
                ("721006562", "Sara Andreza da Silva Rosa Costa dos Santos", "Nova Iguaçu", "50", "100", "+50"),
                ("721007639", "Suellen Siliprandy Sousa", "Nova Iguaçu", "50", "100", "+50"),
                ("721006510", "Tatiana Casemiro Muniz", "Nova Iguaçu", "50", "100", "+50"),
                ("721007547", "Thiago dos Santos Andrade", "Nova Iguaçu", "50", "100", "+50"),
                ("721003367", "Veruma Virgilio Luiz", "Itaperuna", "50", "100", "+50"),
            ]
        },
        {
            "titulo": "2. Fisioterapia em Clínica Médica e Cirúrgica (Cód. 4062) — 8º Período",
            "obs": "10 alterações registradas:",
            "alunos": [
                ("721003623", "Ana Marcia Lisbôa de Oliveira Moreira", "Nova Iguaçu", "70", "100", "+30"),
                ("721003266", "Ariellen Teles Santos de Jesus", "Nova Iguaçu", "70", "100", "+30"),
                ("721003434", "Beatriz Guimarães Lima Ragoso", "Nova Iguaçu", "50", "72", "+22"),
                ("721002915", "Carlos Augusto de Souza Santos", "Nova Iguaçu", "70", "100", "+30"),
                ("721003510", "Fernanda de Carvalho Oliveira", "Nova Iguaçu", "70", "100", "+30"),
                ("721009982", "Flavia Santos Alves Ribeiro", "Nova Iguaçu", "70", "100", "+30"),
                ("721010023", "Maria Jucilene Rodrigues", "Nova Iguaçu", "70", "100", "+30"),
                ("721005277", "Patrícia Souza de Azevedo", "Nova Iguaçu", "70", "100", "+30"),
                ("721002881", "Sandra Auxiliadora Santana Lima", "Nova Iguaçu", "70", "100", "+30"),
                ("721002890", "Victoria B. Botelho", "Nova Iguaçu", "70", "100", "+30"),
            ]
        },
        {
            "titulo": "3. Fisioterapia Dermatofuncional (Cód. 4063) — 8º Período",
            "obs": "10 alterações registradas:",
            "alunos": [
                ("721003623", "Ana Marcia Lisbôa de Oliveira Moreira", "Nova Iguaçu", "70", "78", "+8"),
                ("721003266", "Ariellen Teles Santos de Jesus", "Nova Iguaçu", "70", "78", "+8"),
                ("721003434", "Beatriz Guimarães Lima Ragoso", "Nova Iguaçu", "70", "78", "+8"),
                ("721002915", "Carlos Augusto de Souza Santos", "Nova Iguaçu", "70", "78", "+8"),
                ("721003510", "Fernanda de Carvalho Oliveira", "Nova Iguaçu", "70", "78", "+8"),
                ("721009982", "Flavia Santos Alves Ribeiro", "Nova Iguaçu", "70", "78", "+8"),
                ("721010023", "Maria Jucilene Rodrigues", "Nova Iguaçu", "50", "56", "+6"),
                ("721005277", "Patrícia Souza de Azevedo", "Nova Iguaçu", "70", "78", "+8"),
                ("721002881", "Sandra Auxiliadora Santana Lima", "Nova Iguaçu", "70", "78", "+8"),
                ("721002890", "Victoria B. Botelho", "Nova Iguaçu", "70", "78", "+8"),
            ]
        },
        {
            "titulo": "4. Fisioterapia Cardiovascular (Cód. 4061) — 8º Período",
            "obs": "9 alterações registradas:",
            "alunos": [
                ("721003623", "Ana Marcia Lisbôa de Oliveira Moreira", "Nova Iguaçu", "80", "89", "+9"),
                ("721003434", "Beatriz Guimarães Lima Ragoso", "Nova Iguaçu", "90", "100", "+10"),
                ("721002915", "Carlos Augusto de Souza Santos", "Nova Iguaçu", "90", "100", "+10"),
                ("721003510", "Fernanda de Carvalho Oliveira", "Nova Iguaçu", "90", "100", "+10"),
                ("721009982", "Flavia Santos Alves Ribeiro", "Nova Iguaçu", "90", "100", "+10"),
                ("721010023", "Maria Jucilene Rodrigues", "Nova Iguaçu", "90", "100", "+10"),
                ("721005277", "Patrícia Souza de Azevedo", "Nova Iguaçu", "90", "100", "+10"),
                ("721002881", "Sandra Auxiliadora Santana Lima", "Nova Iguaçu", "90", "100", "+10"),
                ("721002890", "Victoria B. Botelho", "Nova Iguaçu", "90", "100", "+10"),
            ]
        }
    ]

    for d_idx, d_info in enumerate(disciplinas_det):
        p_dtit = doc.add_paragraph()
        p_dtit.paragraph_format.space_before = Pt(6)
        p_dtit.paragraph_format.space_after = Pt(1)
        p_dtit.paragraph_format.keep_with_next = True
        r_dtit = p_dtit.add_run(d_info["titulo"])
        r_dtit.font.name = 'Calibri'; r_dtit.font.size = Pt(9.5); r_dtit.bold = True; r_dtit.font.color.rgb = RGBColor(25, 55, 95)

        p_dobs = doc.add_paragraph()
        p_dobs.paragraph_format.space_before = Pt(0)
        p_dobs.paragraph_format.space_after = Pt(2)
        p_dobs.paragraph_format.keep_with_next = True
        r_dobs = p_dobs.add_run(d_info["obs"])
        r_dobs.font.name = 'Calibri'; r_dobs.font.size = Pt(8.5); r_dobs.italic = True; r_dobs.font.color.rgb = RGBColor(90, 90, 90)

        tbl = doc.add_table(rows=1, cols=6)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl, color="C2D1E0", sz="4")

        hdr_row = tbl.rows[0]
        hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

        for c_idx, h_text in enumerate(headers_det):
            cell = hdr_row.cells[c_idx]
            cell.width = col_w_det[c_idx]
            align = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 1 else WD_ALIGN_PARAGRAPH.CENTER
            format_cell(cell, h_text, bold=True, color_rgb=(255,255,255), align=align, font_size=8, bg_color="275382")

        for r_idx, al_data in enumerate(d_info["alunos"]):
            row = tbl.add_row()
            row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
            
            ra, nome, polo, n_ant, n_nova, var = al_data

            format_cell(row.cells[0], ra, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8, bg_color=bg)
            format_cell(row.cells[1], nome, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=8, bg_color=bg)
            format_cell(row.cells[2], polo, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8, bg_color=bg)
            format_cell(row.cells[3], n_ant, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8, color_rgb=(100,100,100), bg_color=bg)
            format_cell(row.cells[4], n_nova, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, color_rgb=(20,45,85), bg_color=bg)
            format_cell(row.cells[5], var, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8, color_rgb=(0,128,45), bg_color=bg)

    # Salvar nos diretórios
    doc.save(OUTPUT_DOCX)
    print(f"Documento salvo em: {OUTPUT_DOCX}")
    shutil.copyfile(OUTPUT_DOCX, DOWNLOADS_DOCX)
    print(f"Cópia salva em: {DOWNLOADS_DOCX}")

    # Gerar também PDF correspondente
    cmd = ['libreoffice', '--headless', '--convert-to', 'pdf', OUTPUT_DOCX, '--outdir', '/home/hamilcar/Antigravity/Atas de NDE']
    subprocess.run(cmd, capture_output=True, text=True)
    pdf_orig = OUTPUT_DOCX.replace('.docx', '.pdf')
    pdf_down = DOWNLOADS_DOCX.replace('.docx', '.pdf')
    if os.path.exists(pdf_orig):
        shutil.copyfile(pdf_orig, pdf_down)
        print(f"PDF também gerado em: {pdf_orig} e {pdf_down}")

if __name__ == '__main__':
    generate_report()
