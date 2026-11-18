import os
import subprocess
import pandas as pd
import numpy as np
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

TEMPLATE_PATH = '/home/hamilcar/Antigravity/Atas de NDE/templates/timbrado_oficial.docx'
F_OLD = '/home/hamilcar/Downloads/Notas de AD - EAD - 3ª Entrada.xlsx'
F_NEW = '/home/hamilcar/Downloads/delete/ad_ead_notas 2026.2.3.xlsx'
OUTPUT_DOCX = '/home/hamilcar/Antigravity/Atas de NDE/Relatorio_Alteracao_Notas_Fisioterapia_AD_2026.2.docx'
OUTPUT_DIR = '/home/hamilcar/Antigravity/Atas de NDE'

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def set_table_borders(table, color="B0C4DE", sz="4", val="single"):
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

def format_cell(cell, text, bold=False, italic=False, color_rgb=(0,0,0), align=WD_ALIGN_PARAGRAPH.LEFT, font_size=9, bg_color=None):
    if bg_color:
        set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(str(text))
    run.font.name = 'Arial'
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def load_and_compare_data():
    df_old = pd.read_excel(F_OLD)
    df_new = pd.read_excel(F_NEW)

    def norm_code(x):
        try: return str(int(str(x).strip()))
        except: return str(x).strip()

    df_old['CodigoNorm'] = df_old['CodigoDisciplina'].apply(norm_code)
    df_new['CodigoNorm'] = df_new['CodigoDisciplina'].apply(norm_code)
    df_old['RA'] = df_old['RA'].astype(str)
    df_new['RA'] = df_new['RA'].astype(str)

    fisio_old = df_old[df_old['CursoMatricula'].str.contains('Fisioterapia', case=False, na=False)].copy()
    fisio_new = df_new[df_new['CursoMatricula'].str.contains('Fisioterapia', case=False, na=False)].copy()

    m = pd.merge(fisio_old, fisio_new, on=['RA', 'CodigoNorm'], suffixes=('_old', '_new'))

    diffs = []
    for idx, r in m.iterrows():
        n_old = r['Nota_old']
        n_new = r['Nota_new']
        if pd.isna(n_old) and pd.isna(n_new):
            continue
        elif pd.isna(n_old) or pd.isna(n_new) or float(n_old) != float(n_new):
            diffs.append({
                'Disciplina': r['Disciplina_new'],
                'Codigo': r['CodigoDisciplina_new'],
                'Periodo': int(r['Período_new']),
                'RA': r['RA'],
                'Nome': r['Nome_new'],
                'Polo': r['CampusPolo_new'],
                'Nota_Anterior': int(r['Nota_old']) if not pd.isna(r['Nota_old']) else None,
                'Nota_Nova': int(r['Nota_new']) if not pd.isna(r['Nota_new']) else None,
                'Variacao': int(r['Nota_new'] - r['Nota_old'])
            })

    return fisio_new, pd.DataFrame(diffs).sort_values(by=['Disciplina', 'Nome'])

def build_docx(df_total_fisio, df_diffs):
    doc = docx.Document(TEMPLATE_PATH)

    # Limpar parágrafos vazios iniciais
    for p in list(doc.paragraphs):
        p._p.getparent().remove(p._p)

    # Configurar rodapé
    section = doc.sections[0]
    footer = section.footer
    footer_p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    footer_p.text = ''
    footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_run = footer_p.add_run("Relatório de Alterações de Notas – Fisioterapia | Avaliação Diagnóstica 2026.2")
    f_run.font.name = 'Arial'
    f_run.font.size = Pt(8.5)
    f_run.font.color.rgb = RGBColor(100, 100, 100)

    # Cabeçalho do Relatório
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(4)
    title_p.paragraph_format.space_after = Pt(2)
    r_inst = title_p.add_run("UNIVERSIDADE IGUAÇU – UNIG\n")
    r_inst.font.name = 'Arial'
    r_inst.font.size = Pt(11)
    r_inst.bold = True
    r_inst.font.color.rgb = RGBColor(31, 73, 125)

    r_subinst = title_p.add_run("CURSO DE FISIOTERAPIA | NÚCLEO DOCENTE ESTRUTURANTE E COLEGIADO\n")
    r_subinst.font.name = 'Arial'
    r_subinst.font.size = Pt(9.5)
    r_subinst.bold = True
    r_subinst.font.color.rgb = RGBColor(80, 80, 80)

    r_title = title_p.add_run("RELATÓRIO TÉCNICO DE CONFERÊNCIA E ALTERAÇÃO DE NOTAS\n")
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(13)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(20, 45, 80)

    r_ad = title_p.add_run("AVALIAÇÃO DIAGNÓSTICA (AD) – SEMESTRE LETIVO 2026.2 (3ª ENTRADA)")
    r_ad.font.name = 'Arial'
    r_ad.font.size = Pt(10.5)
    r_ad.bold = True
    r_ad.font.color.rgb = RGBColor(50, 50, 50)

    # Linha divisória fina
    div_p = doc.add_paragraph()
    div_p.paragraph_format.space_before = Pt(2)
    div_p.paragraph_format.space_after = Pt(6)
    div_run = div_p.add_run("―" * 58)
    div_run.font.name = 'Arial'
    div_run.font.size = Pt(9)
    div_run.font.color.rgb = RGBColor(180, 180, 180)
    div_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Tabela 1: Metadados Executivos
    meta_table = doc.add_table(rows=3, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table, color="1F497D", sz="6")

    meta_info = [
        ("Curso:", "Fisioterapia (Bacharelado)", "Modalidade / Entrada:", "EAD / Semipresencial – 2026.2 (3ª Entrada)"),
        ("Data de Emissão:", "04 de novembro de 2026", "Total de Matrículas Avaliadas:", f"{len(df_total_fisio)} registros"),
        ("Total de Notas Alteradas:", f"{len(df_diffs)} notas", "Total de Alunos Beneficiados:", f"{df_diffs['Nome'].nunique()} alunos distintos")
    ]

    for row_idx, (k1, v1, k2, v2) in enumerate(meta_info):
        c0 = meta_table.cell(row_idx, 0)
        c1 = meta_table.cell(row_idx, 1)
        format_cell(c0, f"{k1} {v1}", bold=False, font_size=9, bg_color="F4F7FA")
        c0.paragraphs[0].runs[0].bold = True # apenas chave
        # refinar
        c0.text = ''
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r_k1 = p0.add_run(k1 + " ")
        r_k1.bold = True
        r_k1.font.name = 'Arial'; r_k1.font.size = Pt(9)
        r_v1 = p0.add_run(v1)
        r_v1.bold = False
        r_v1.font.name = 'Arial'; r_v1.font.size = Pt(9)

        c1.text = ''
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r_k2 = p1.add_run(k2 + " ")
        r_k2.bold = True
        r_k2.font.name = 'Arial'; r_k2.font.size = Pt(9)
        r_v2 = p1.add_run(v2)
        r_v2.bold = False
        r_v2.font.name = 'Arial'; r_v2.font.size = Pt(9)
        set_cell_background(c0, "F2F5F8")
        set_cell_background(c1, "F2F5F8")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

    # 1. Contextualização
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(4)
    r = h1.add_run("1. OBJETIVO E METODOLOGIA DA CONFERÊNCIA")
    r.font.name = 'Arial'; r.font.size = Pt(11); r.bold = True; r.font.color.rgb = RGBColor(31, 73, 125)

    p_ctx = doc.add_paragraph()
    p_ctx.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_ctx.paragraph_format.space_before = Pt(2)
    p_ctx.paragraph_format.space_after = Pt(6)
    p_ctx.paragraph_format.line_spacing = 1.15
    run_ctx = p_ctx.add_run(
        "O presente relatório técnico tem por objetivo consolidar e auditar oficialmente as alterações de notas "
        "ocorridas nas avaliações diagnósticas (AD) dos alunos matriculados no curso de Fisioterapia da Universidade Iguaçu (UNIG), "
        "referentes ao semestre 2026.2 (3ª Entrada). A análise comparativa foi realizada confrontando a base histórica de fechamento inicial "
        "com a base consolidada pós-recursos e anulações de itens de prova."
    )
    run_ctx.font.name = 'Arial'; run_ctx.font.size = Pt(9.5)

    p_obs = doc.add_paragraph()
    p_obs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_obs.paragraph_format.space_before = Pt(2)
    p_obs.paragraph_format.space_after = Pt(8)
    p_obs.paragraph_format.line_spacing = 1.15
    run_obs = p_obs.add_run(
        "Constatou-se que todas as 42 alterações identificadas resultaram em acréscimo de pontuação para os discentes, "
        "decorrentes da procedência de recursos acadêmicos e revisão das chaves de correção nas disciplinas afetadas. "
        "Ademais, os arquivos recentemente extraídos nesta data confirmam a estabilidade e integridade da base após os devidos ajustes."
    )
    run_obs.font.name = 'Arial'; run_obs.font.size = Pt(9.5)

    # 2. Resumo por Disciplina
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(4)
    r2 = h2.add_run("2. QUADRO RESUMO DE ALTERAÇÕES POR DISCIPLINA")
    r2.font.name = 'Arial'; r2.font.size = Pt(11); r2.bold = True; r2.font.color.rgb = RGBColor(31, 73, 125)

    summary_tbl = doc.add_table(rows=1, cols=5)
    summary_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(summary_tbl, color="1F497D", sz="4")

    headers_summary = ["Código", "Disciplina", "Período", "Alunos Impactados", "Padrão de Majoração"]
    col_widths_sum = [Inches(0.8), Inches(2.8), Inches(0.8), Inches(1.1), Inches(1.6)]

    for c_idx, h_text in enumerate(headers_summary):
        cell = summary_tbl.cell(0, c_idx)
        cell.width = col_widths_sum[c_idx]
        format_cell(cell, h_text, bold=True, color_rgb=(255,255,255), align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9, bg_color="1F497D")

    summary_data = [
        ("1313", "Fisioterapia Ortopédica e Tramatológica", "6º", "13", "50 ➔ 100 (+50) / 40 ➔ 80 (+40)"),
        ("4062", "Fisioterapia em Clínica Médica e Cirúrgica", "8º", "10", "70 ➔ 100 (+30) / 50 ➔ 72 (+22)"),
        ("4063", "Fisioterapia Dermatofuncional", "8º", "10", "70 ➔ 78 (+8) / 50 ➔ 56 (+6)"),
        ("4061", "Fisioterapia Cardiovascular", "8º", "9", "90 ➔ 100 (+10) / 80 ➔ 89 (+9)"),
    ]

    for row_idx, r_data in enumerate(summary_data):
        row = summary_tbl.add_row()
        bg = "FFFFFF" if row_idx % 2 == 0 else "F7F9FB"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.width = col_widths_sum[c_idx]
            align = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 1 else WD_ALIGN_PARAGRAPH.CENTER
            bold = True if c_idx in [0, 3] else False
            format_cell(cell, val, bold=bold, align=align, font_size=8.5, bg_color=bg)

    # Linha totalizadora
    tot_row = summary_tbl.add_row()
    for c_idx in range(5):
        cell = tot_row.cells[c_idx]
        cell.width = col_widths_sum[c_idx]
        set_cell_background(cell, "EBF0F5")
    format_cell(tot_row.cells[1], "TOTAL DE ALTERAÇÕES", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, font_size=9, bg_color="EBF0F5")
    format_cell(tot_row.cells[3], "42", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9.5, color_rgb=(31,73,125), bg_color="EBF0F5")
    format_cell(tot_row.cells[4], "4 disciplinas impactadas", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color="EBF0F5")

    # 3. Detalhamento por Disciplina
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(4)
    r3 = h3.add_run("3. DETALHAMENTO NOMINAL DAS NOTAS ALTERADAS POR DISCIPLINA")
    r3.font.name = 'Arial'; r3.font.size = Pt(11); r3.bold = True; r3.font.color.rgb = RGBColor(31, 73, 125)

    headers_detail = ["RA", "Nome do Aluno", "Polo", "Nota Anterior", "Nota Nova", "Variação"]
    col_widths_det = [Inches(1.0), Inches(2.7), Inches(1.1), Inches(0.9), Inches(0.9), Inches(0.8)]

    # Ordenar disciplinas: Ortopédica, Clínica Médica, Dermatofuncional, Cardiovascular
    ordem_disc = [
        "Fisioterapia Ortopédica e Tramatológica",
        "Fisioterapia em Clínica Médica e Cirúrgica",
        "Fisioterapia Dermatofuncional",
        "Fisioterapia Cardiovascular"
    ]

    sub_sec_idx = 1
    for disc_name in ordem_disc:
        grp = df_diffs[df_diffs['Disciplina'] == disc_name].sort_values(by='Nome')
        if len(grp) == 0:
            continue
        
        cod_disc = grp.iloc[0]['Codigo']
        per_disc = grp.iloc[0]['Periodo']

        sub_p = doc.add_paragraph()
        sub_p.paragraph_format.space_before = Pt(10)
        sub_p.paragraph_format.space_after = Pt(3)
        sub_p.paragraph_format.keep_with_next = True
        r_sub = sub_p.add_run(f"3.{sub_sec_idx}. {disc_name} (Código: {cod_disc} – {per_disc}º Período) – {len(grp)} alunos")
        r_sub.font.name = 'Arial'; r_sub.font.size = Pt(10); r_sub.bold = True; r_sub.font.color.rgb = RGBColor(20, 50, 90)

        tbl = doc.add_table(rows=1, cols=6)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl, color="C0D0E0", sz="4")

        for c_idx, h_text in enumerate(headers_detail):
            cell = tbl.cell(0, c_idx)
            cell.width = col_widths_det[c_idx]
            format_cell(cell, h_text, bold=True, color_rgb=(255,255,255), align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color="244C78")

        for r_idx, (_, row_data) in enumerate(grp.iterrows()):
            r_elm = tbl.add_row()
            bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
            
            ra_val = str(row_data['RA'])
            nome_val = str(row_data['Nome'])
            polo_val = str(row_data['Polo'])
            n_ant = f"{row_data['Nota_Anterior']}"
            n_nova = f"{row_data['Nota_Nova']}"
            diff_val = f"+{row_data['Variacao']}" if row_data['Variacao'] > 0 else f"{row_data['Variacao']}"

            format_cell(r_elm.cells[0], ra_val, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color=bg)
            format_cell(r_elm.cells[1], nome_val, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=8.5, bg_color=bg)
            format_cell(r_elm.cells[2], polo_val, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color=bg)
            format_cell(r_elm.cells[3], n_ant, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, color_rgb=(100,100,100), bg_color=bg)
            format_cell(r_elm.cells[4], n_nova, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9, color_rgb=(20,40,80), bg_color=bg)
            format_cell(r_elm.cells[5], diff_val, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, color_rgb=(0,120,40), bg_color=bg)

        sub_sec_idx += 1

    # 4. Visão Consolidada por Aluno
    doc.add_page_break()

    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(8)
    h4.paragraph_format.space_after = Pt(4)
    r4 = h4.add_run("4. CONSOLIDADO POR DISCENTE BENEFICIADO")
    r4.font.name = 'Arial'; r4.font.size = Pt(11); r4.bold = True; r4.font.color.rgb = RGBColor(31, 73, 125)

    p_cons_intro = doc.add_paragraph()
    p_cons_intro.paragraph_format.space_before = Pt(2)
    p_cons_intro.paragraph_format.space_after = Pt(6)
    p_cons_intro.paragraph_format.line_spacing = 1.15
    r_ci = p_cons_intro.add_run(
        "A relação a seguir consolida os 23 discentes que obtiveram reajuste em suas notas de Avaliação Diagnóstica, "
        "indicando as respectivas disciplinas e o status final de cada avaliação:"
    )
    r_ci.font.name = 'Arial'; r_ci.font.size = Pt(9.5)

    cons_tbl = doc.add_table(rows=1, cols=5)
    cons_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(cons_tbl, color="1F497D", sz="4")

    headers_cons = ["RA", "Nome do Aluno", "Polo", "Per.", "Disciplinas e Alterações de Notas (De ➔ Para)"]
    col_widths_c = [Inches(1.0), Inches(2.2), Inches(1.0), Inches(0.5), Inches(2.6)]

    for c_idx, h_text in enumerate(headers_cons):
        cell = cons_tbl.cell(0, c_idx)
        cell.width = col_widths_c[c_idx]
        format_cell(cell, h_text, bold=True, color_rgb=(255,255,255), align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color="1F497D")

    alunos_unicos = sorted(df_diffs['Nome'].unique())
    for r_idx, aluno_nome in enumerate(alunos_unicos):
        sub_aluno = df_diffs[df_diffs['Nome'] == aluno_nome]
        r_row = cons_tbl.add_row()
        bg = "FFFFFF" if r_idx % 2 == 0 else "F7F9FB"

        ra = sub_aluno.iloc[0]['RA']
        polo = sub_aluno.iloc[0]['Polo']
        per = str(sub_aluno.iloc[0]['Periodo'])

        discs_text_list = []
        for _, disc_r in sub_aluno.iterrows():
            d_short = disc_r['Disciplina'].replace('Fisioterapia em ', '').replace('Fisioterapia ', '')
            discs_text_list.append(f"• {d_short}: {disc_r['Nota_Anterior']} ➔ {disc_r['Nota_Nova']} (+{disc_r['Variacao']})")
        discs_text = "\n".join(discs_text_list)

        format_cell(r_row.cells[0], ra, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color=bg)
        format_cell(r_row.cells[1], aluno_nome, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=8.5, bg_color=bg)
        format_cell(r_row.cells[2], polo, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color=bg)
        format_cell(r_row.cells[3], f"{per}º", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8.5, bg_color=bg)
        format_cell(r_row.cells[4], discs_text, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=8, bg_color=bg)

    # 5. Validação e Assinatura
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(16)
    h5.paragraph_format.space_after = Pt(4)
    h5.paragraph_format.keep_with_next = True
    r5 = h5.add_run("5. CONCLUSÃO E VALIDAÇÃO")
    r5.font.name = 'Arial'; r5.font.size = Pt(11); r5.bold = True; r5.font.color.rgb = RGBColor(31, 73, 125)

    p_concl = doc.add_paragraph()
    p_concl.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_concl.paragraph_format.space_before = Pt(2)
    p_concl.paragraph_format.space_after = Pt(25)
    p_concl.paragraph_format.line_spacing = 1.15
    r_cc = p_concl.add_run(
        "Certifica-se que todas as alterações acima elencadas foram auditadas e refletem rigorosamente "
        "o espelho das correções homologadas. As novas notas passam a vigorar nos assentamentos acadêmicos "
        "e nas atas oficiais de NDE e Colegiado do Curso de Fisioterapia."
    )
    r_cc.font.name = 'Arial'; r_cc.font.size = Pt(9.5)

    # Bloco de Assinaturas
    sign_table = doc.add_table(rows=1, cols=2)
    sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(sign_table, color="FFFFFF", sz="0", val="none")

    c_sign1 = sign_table.cell(0, 0)
    c_sign2 = sign_table.cell(0, 1)

    format_cell(c_sign1, "_________________________________________\nCoordenação do Curso de Fisioterapia\nUniversidade Iguaçu – UNIG", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9)
    format_cell(c_sign2, "_________________________________________\nNúcleo Docente Estruturante (NDE)\nCurso de Fisioterapia – UNIG", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9)

    # Salvar documento
    doc.save(OUTPUT_DOCX)
    print(f"Relatório DOCX salvo com sucesso em: {OUTPUT_DOCX}")

    # Gerar PDF
    cmd = ['libreoffice', '--headless', '--convert-to', 'pdf', OUTPUT_DOCX, '--outdir', OUTPUT_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        pdf_path = OUTPUT_DOCX.replace('.docx', '.pdf')
        print(f"Relatório PDF gerado com sucesso em: {pdf_path}")
    else:
        print(f"Aviso na conversão para PDF: {res.stderr}")

if __name__ == '__main__':
    df_tot, df_d = load_and_compare_data()
    print(f"Carregados {len(df_tot)} registros de Fisioterapia e {len(df_d)} notas alteradas.")
    build_docx(df_tot, df_d)
