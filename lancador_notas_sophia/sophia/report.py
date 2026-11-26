from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .data import grade_value

HEADERS = ["Linha de origem", "Aluno", "RA", "Curso", "Polo", "Turma", "Etapa", "Disciplina", "Avaliação", "Nota", "Status / Motivo"]
_COLUMN_WIDTHS = (18, 38, 18, 36, 22, 40, 18, 48, 14, 14, 65)
_HEADER_FONT = Font(color="FFFFFF", bold=True)
_HEADER_FILL = PatternFill("solid", fgColor="24556B")
_HEADER_ALIGNMENT = Alignment(wrap_text=True, vertical="center")
_CELL_ALIGNMENT = Alignment(vertical="top", wrap_text=True)


def safe_cell(value):
    # Conteúdo da planilha/portal é texto, nunca fórmula executável.
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_report(folder: Path, results: list[dict], pending: list[dict], absent: list[dict], partial: bool) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S_%f")
    path = folder / f"relatorio_notas_{stamp}{'_parcial' if partial else ''}.xlsx"
    book = Workbook()
    book.remove(book.active)
    for title, rows in (("Resultados", results), ("Planilha - Pendentes", pending), ("Web - Sem Planilha", absent)):
        sheet = book.create_sheet(title)
        sheet.append(HEADERS)
        for row in rows:
            values = [safe_cell(row.get(h, "")) for h in HEADERS]
            try:
                grade = grade_value(row.get("Nota", ""), max_grade=100)
                if grade is not None:
                    values[9] = float(grade.replace(",", "."))
            except ValueError:
                pass  # Preservar o texto original de notas inválidas nas pendências.
            sheet.append(values)
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        sheet.row_dimensions[1].height = 30
        for cell in sheet[1]:
            cell.font = _HEADER_FONT
            cell.fill = _HEADER_FILL
            cell.alignment = _HEADER_ALIGNMENT
        for idx, width in enumerate(_COLUMN_WIDTHS, 1):
            sheet.column_dimensions[get_column_letter(idx)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = _CELL_ALIGNMENT
            for idx in (2, 3):
                row[idx - 1].number_format = "@"
            row[9].number_format = "0.##########"
    temporary = path.with_suffix(".tmp")
    try:
        book.save(temporary)
        temporary.replace(path)
    finally:
        book.close()
        if temporary.exists():
            temporary.unlink()
    return path
