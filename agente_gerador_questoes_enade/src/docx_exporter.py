# -*- coding: utf-8 -*-
"""
Exportador de Questões ENADE para Microsoft Word (.docx).
Converte o entregável bifurcado (Versão do Estudante e Versão do Professor) em arquivos .docx formatados.
Suporta:
- Diagramas em código monoespaçado (Consolas 8.5pt, alinhamento preservado)
- Conversão automática completa de fórmulas LaTeX e matemática em símbolos Unicode limpos (n₁, n₂, θ₁, θ₂, θ_c, I²R, λ, µm, m², ·, sin, arcsin)
- Formatador Markdown Inline: **negrito**, *itálico*, ***negrito itálico*** e `código` (remove asteriscos no Word)
- Tabelas Markdown convertidas em tabelas nativas do Word com cabeçalho sombreado
"""
import os, re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

class ENADEDocxExporter:
    def __init__(self):
        pass

    def _clean_str(self, s):
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)

    def _convert_math_to_unicode(self, text):
        """
        Converte notações LaTeX e matemáticas em símbolos Unicode limpos para o Word.
        """
        if not text:
            return text
        
        # 1. Substituir \theta e escapamentos \t + heta
        text = re.sub(r'\\t\s*heta|\t\s*heta|\\+theta', 'θ', text)
        text = text.replace(r'\theta', 'θ').replace('\theta', 'θ')
        
        # 2. Substituir \cdot, \sin, \cos, \arcsin, \lambda, \mu, \pi
        text = text.replace(r'\cdot', '·').replace('\\cdot', '·')
        text = text.replace(r'\sin', 'sin').replace('\\sin', 'sin')
        text = text.replace(r'\cos', 'cos').replace('\\cos', 'cos')
        text = text.replace(r'\arcsin', 'arcsin').replace('\\arcsin', 'arcsin')
        text = text.replace(r'\lambda', 'λ').replace('\\lambda', 'λ')
        text = text.replace(r'\mu', 'µ').replace('\\mu', 'µ')
        text = text.replace(r'\pi', 'π').replace('\\pi', 'π')
        text = text.replace(r'\text{m}', 'm').replace(r'\text{ m}', ' m').replace(r'\text{m}^2', 'm²')
        
        # 3. Subscritos (_0 a _9)
        sub_map = {
            '_0': '₀', '_1': '₁', '_2': '₂', '_3': '₃', '_4': '₄',
            '_5': '₅', '_6': '₆', '_7': '₇', '_8': '₈', '_9': '₉'
        }
        for sub_str, uni in sub_map.items():
            text = text.replace(sub_str, uni)
            
        # 4. Sobrescritos (^0 a ^9)
        sup_map = {
            '^0': '⁰', '^1': '¹', '^2': '²', '^3': '³', '^4': '⁴',
            '^5': '⁵', '^6': '⁶', '^7': '⁷', '^8': '⁸', '^9': '⁹'
        }
        for sup_str, uni in sup_map.items():
            text = text.replace(sup_str, uni)
            
        # Limpar cifrões remanescentes
        text = text.replace('$', '')
        return text

    def markdown_to_docx(self, markdown_text: str, output_docx_path: str, title: str = "Questão ENADE"):
        doc = docx.Document()
        
        # Configurar margens (1 polegada / 2.54 cm)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
        # Adicionar Título Principal
        h1 = doc.add_heading(title, level=0)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        lines = markdown_text.splitlines()
        in_code_block = False
        table_buffer = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_str = line.rstrip()
            
            # 1. Tratar Blocos de Código (Diagramas ASCII / Esquemas)
            if line_str.startswith("```"):
                if in_code_block:
                    in_code_block = False
                else:
                    in_code_block = True
                i += 1
                continue
                
            if in_code_block:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                run = p.add_run(line)  # Preserva os espaços originais para alinhamento ASCII
                run.font.name = 'Consolas'
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
                i += 1
                continue
                
            # 2. Tratar Tabelas Markdown (linhas com |)
            if line_str.startswith("|") and line_str.endswith("|"):
                table_buffer.append(line_str)
                i += 1
                continue
            else:
                if table_buffer:
                    self._render_table(doc, table_buffer)
                    table_buffer = []

            if not line_str.strip():
                i += 1
                continue
                
            # Converter matemática LaTeX para Unicode
            clean_line = self._convert_math_to_unicode(line_str.strip())
            
            if clean_line.startswith("# "):
                doc.add_heading(clean_line[2:], level=1)
            elif clean_line.startswith("## "):
                doc.add_heading(clean_line[3:], level=2)
            elif clean_line.startswith("### "):
                doc.add_heading(clean_line[4:], level=3)
            elif clean_line.startswith("#### "):
                doc.add_heading(clean_line[5:], level=4)
            elif clean_line.startswith("* ") or clean_line.startswith("- "):
                p = doc.add_paragraph(style="List Bullet")
                self._add_formatted_text(p, clean_line[2:])
            elif re.match(r"^\d+\.\s", clean_line):
                p = doc.add_paragraph(style="List Number")
                num_prefix = re.match(r"^\d+\.\s", clean_line).group(0)
                self._add_formatted_text(p, clean_line[len(num_prefix):])
            else:
                p = doc.add_paragraph()
                self._add_formatted_text(p, clean_line)
                
            i += 1

        # Processar tabela remanescente no final do arquivo
        if table_buffer:
            self._render_table(doc, table_buffer)
            
        doc.save(output_docx_path)
        print(f"[DOCX EXPORTER] Arquivo Word gerado com sucesso: {output_docx_path}")
        return output_docx_path

    def _render_table(self, doc, table_lines):
        """
        Converte linhas de tabela Markdown em tabela nativa do Word com estilo.
        """
        rows_data = []
        for line in table_lines:
            # Ignorar linha separadora de cabeçalho | --- | --- |
            if re.match(r"^\|(\s*:?-+:?\s*\|)+$", line.strip()):
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            rows_data.append(cols)
            
        if not rows_data:
            return
            
        num_rows = len(rows_data)
        num_cols = max(len(r) for r in rows_data)
        
        table = doc.add_table(rows=num_rows, cols=num_cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        
        for r_idx, row in enumerate(rows_data):
            for c_idx, val in enumerate(row):
                if c_idx < num_cols:
                    cell = table.cell(r_idx, c_idx)
                    cell.text = ""
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    
                    # Se for linha de cabeçalho (r_idx == 0)
                    if r_idx == 0:
                        shading_elm = parse_xml(r'<w:shd {} w:fill="003366"/>'.format(nsdecls('w')))
                        cell._tc.get_or_add_tcPr().append(shading_elm)
                        run = p.add_run(self._convert_math_to_unicode(val))
                        run.bold = True
                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    else:
                        if r_idx % 2 == 1:
                            shading_elm = parse_xml(r'<w:shd {} w:fill="F2F4F7"/>'.format(nsdecls('w')))
                            cell._tc.get_or_add_tcPr().append(shading_elm)
                        self._add_formatted_text(p, self._convert_math_to_unicode(val))

    def _add_formatted_text(self, paragraph, text):
        text = self._clean_str(text)
        pattern = r"(\*\*\*[^\*]+\*\*\*|\*\*[^\*]+\*\*|\*[^\*]+\*|`[^`]+`)"
        parts = re.split(pattern, text)
        
        for part in parts:
            if not part:
                continue
            clean_part = self._clean_str(part)
            if clean_part.startswith("***") and clean_part.endswith("***"):
                run = paragraph.add_run(clean_part[3:-3])
                run.bold = True
                run.italic = True
            elif clean_part.startswith("**") and clean_part.endswith("**"):
                run = paragraph.add_run(clean_part[2:-2])
                run.bold = True
            elif clean_part.startswith("*") and clean_part.endswith("*"):
                run = paragraph.add_run(clean_part[1:-1])
                run.italic = True
            elif clean_part.startswith("`") and clean_part.endswith("`"):
                run = paragraph.add_run(clean_part[1:-1])
                run.font.name = 'Consolas'
                run.font.size = Pt(9.5)
            else:
                paragraph.add_run(clean_part)
