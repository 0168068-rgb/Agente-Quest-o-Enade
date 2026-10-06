# -*- coding: utf-8 -*-
"""
Exportador de Questões ENADE para Microsoft Word (.docx).
Converte o entregável bifurcado (Versão do Estudante e Versão do Professor) em arquivos .docx formatados.
"""
import os, re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

class ENADEDocxExporter:
    def __init__(self):
        pass

    def markdown_to_docx(self, markdown_text: str, output_docx_path: str, title: str = "Questão ENADE"):
        doc = docx.Document()
        
        # Configurar margens
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
        # Adicionar Título
        h1 = doc.add_heading(title, level=0)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        lines = markdown_text.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            
            if line_str.startswith("# "):
                h = doc.add_heading(line_str[2:], level=1)
            elif line_str.startswith("## "):
                h = doc.add_heading(line_str[3:], level=2)
            elif line_str.startswith("### "):
                h = doc.add_heading(line_str[4:], level=3)
            elif line_str.startswith("#### "):
                h = doc.add_heading(line_str[5:], level=4)
            elif line_str.startswith("* ") or line_str.startswith("- "):
                p = doc.add_paragraph(style="List Bullet")
                self._add_formatted_text(p, line_str[2:])
            elif line_str.startswith("1. ") or line_str.startswith("2. ") or line_str.startswith("3. "):
                p = doc.add_paragraph(style="List Number")
                self._add_formatted_text(p, line_str[3:])
            else:
                p = doc.add_paragraph()
                self._add_formatted_text(p, line_str)
                
        doc.save(output_docx_path)
        print(f"[DOCX EXPORTER] Arquivo Word gerado com sucesso: {output_docx_path}")
        return output_docx_path

    def _add_formatted_text(self, paragraph, text):
        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                run = paragraph.add_run(part[2:-2])
                run.bold = True
            else:
                paragraph.add_run(part)
