# -*- coding: utf-8 -*-
"""
Gerador Mestre Automatizado de Provas AI 2026-4 para as 22 Disciplinas do NEAD.
Gera os arquivos .docx e .xlsx para cada disciplina diretamente nas respectivas pastas 'Provas 2026-4/AI'.
"""
import os, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

sys.path.append('/home/hamilcar/Antigravity/agente_gerador_questoes_enade/src')
from docx_exporter import ENADEDocxExporter

nead_base = '/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD'

def create_discipline_exam(folder_name, discipline_name, file_title, uas_str, questions):
    target_dir = os.path.join(nead_base, folder_name, 'Provas 2026-4', 'AI')
    os.makedirs(target_dir, exist_ok=True)
    
    # ---------------------------------------------------------
    # 1. MONTAR CONTEÚDO MARKDOWN PARA O WORD (.DOCX)
    # ---------------------------------------------------------
    md_lines = [
        f"# BANCO DE QUESTÕES ENADE — {discipline_name.upper()}",
        "## CADERNO DE QUESTÕES (VERSÃO DO ESTUDANTE)",
        "\n---\n"
    ]
    
    for idx, q in enumerate(questions, 1):
        md_lines.append(f"## QUESTÃO {idx} (UA {q['ua']} — {q['kw']})")
        md_lines.append(f"**Tipo Estrutural:** {q['tipo_label']}\n")
        md_lines.append("### Contexto Realista")
        md_lines.append(q['context_text'])
        
        if q.get('afirmativas'):
            md_lines.append("\n### Afirmativas para Análise")
            md_lines.append(q['afirmativas'])
            
        md_lines.append("\n### Comando da Questão")
        md_lines.append(q['comando_text'])
        md_lines.append(f"\nA) {q['opt_a']}  ")
        md_lines.append(f"B) {q['opt_b']}  ")
        md_lines.append(f"C) {q['opt_c']}  ")
        md_lines.append(f"D) {q['opt_d']}  ")
        md_lines.append("\n---\n")
        
    md_content = "\n".join(md_lines)
    output_docx = os.path.join(target_dir, f"{file_title}.docx")
    exporter = ENADEDocxExporter()
    exporter.markdown_to_docx(md_content, output_docx, title=f"Caderno de Questões ENADE - {discipline_name}")
    print(f"[DOCX OK] {output_docx}")

    # ---------------------------------------------------------
    # 2. MONTAR PLANILHA EXCEL (.XLSX)
    # ---------------------------------------------------------
    excel_rows = [
        ["Identificação da questão", "Palavra chave", "Tipo da questão", "Nível cognitivo", "Texto da Questão", "Alternativa A", "Alternativa B", "Alternativa C", "Alternativa D", "Feedback da questão"]
    ]
    
    for idx, q in enumerate(questions, 1):
        ident = f"UA-{q['ua']}_QUESTÃO-{idx}_OBJ-{q['obj']}_{q['grau']}"
        texto_q = f"Disciplina: {discipline_name}\n\n{q['context_text']}"
        if q.get('afirmativas'):
            texto_q += f"\n\n{q['afirmativas']}"
        texto_q += f"\n\nPergunta: {q['comando_text']}"
        
        excel_rows.append([
            ident,
            q['kw'],
            q['tipo_excel'],
            q['nivel_excel'],
            texto_q,
            q['opt_a'],
            q['opt_b'],
            q['opt_c'],
            q['opt_d'],
            q['feedback']
        ])
        
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Questões ENADE"
    
    header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    cell_font = Font(name="Calibri", size=10)
    wrap_alignment = Alignment(wrap_text=True, vertical="top")
    thin_border = Border(
        left=Side(style='thin', color='D3D3D3'),
        right=Side(style='thin', color='D3D3D3'),
        top=Side(style='thin', color='D3D3D3'),
        bottom=Side(style='thin', color='D3D3D3')
    )
    
    for r_idx, r_data in enumerate(excel_rows, 1):
        for c_idx, val in enumerate(r_data, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.border = thin_border
            if r_idx == 1:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            else:
                cell.font = cell_font
                cell.alignment = wrap_alignment
                
    col_widths = [28, 30, 28, 20, 65, 40, 40, 40, 40, 65]
    for idx, width in enumerate(col_widths, 1):
        col_letter = openpyxl.utils.get_column_letter(idx)
        ws.column_dimensions[col_letter].width = width
        
    output_xlsx = os.path.join(target_dir, f"{file_title}.xlsx")
    wb.save(output_xlsx)
    print(f"[EXCEL OK] {output_xlsx}")

print("Módulo gerador carregado.")
