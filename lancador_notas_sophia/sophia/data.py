from __future__ import annotations

import csv
import io
import math
import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

_COURSE_STOP_WORDS = frozenset({
    "SUPERIOR", "TECNOLOGIA", "TECNOLOGO", "GRADUACAO", "EAD",
    "BACHARELADO", "LICENCIATURA", "CURSO", "DE", "DA", "DO", "DOS", "DAS", "EM", "E",
})
_COURSE_TOKEN_RE = re.compile(r"(\w+)(\.*)")


@lru_cache(maxsize=16384)
def _normalize_str(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return " ".join("".join(c for c in decomposed if unicodedata.category(c) != "Mn").upper().split())


def normalize(value) -> str:
    if isinstance(value, str):
        return _normalize_str(value)
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    if pd.isna(value):
        return ""
    return _normalize_str(str(value))


def identifier(value) -> str:
    text = str(value if value is not None else "").strip()
    # Excel pode representar uma matrícula numérica como 12345.0.
    return re.sub(r"\.0$", "", text)


@lru_cache(maxsize=4096)
def _unit_name_norm(text: str) -> str:
    text = "".join("-" if unicodedata.category(c) == "Pd" or c == "−" else c for c in text)
    text = re.sub(r"^(POLO|CAMPUS|UNIDADE)\s+", "", text)
    return re.sub(r"\s*[-/]\s*[A-Z]{2}$", "", text).strip()


def unit_name(value) -> str:
    return _unit_name_norm(normalize(value))


def usable_unit(value) -> bool:
    text = normalize(value)
    return bool(text and not text.isdigit() and text not in {"TRUE", "FALSE", "NAN"}
                and not text.startswith(("NOTA ", "EXPORTAD", "NAO EXPORTAD")))


@lru_cache(maxsize=8192)
def _course_in_class_norm(a: str, b: str) -> bool:
    if b and b in a:
        return True
    label_tokens = [(m.group(1), bool(m.group(2))) for m in _COURSE_TOKEN_RE.finditer(a)]
    course_tokens = [(m.group(1), bool(m.group(2))) for m in _COURSE_TOKEN_RE.finditer(b)]
    words = [(w, dot) for w, dot in course_tokens if w not in _COURSE_STOP_WORDS] or course_tokens
    if not words or not label_tokens:
        return False

    def matches(course_word: str, course_dot: bool, label_word: str, label_dot: bool) -> bool:
        if course_word == label_word:
            return True
        if (len(label_word) >= 3 or (label_dot and len(label_word) >= 2)) and course_word.startswith(label_word):
            return True
        if (len(course_word) >= 3 or (course_dot and len(course_word) >= 2)) and label_word.startswith(course_word):
            return True
        return False

    return all(any(matches(w, w_dot, t, t_dot) for t, t_dot in label_tokens) for w, w_dot in words)


def course_in_class(label: str, course: str) -> bool:
    return _course_in_class_norm(normalize(label), normalize(course))


def grade_value(value, *, max_grade: int = 10) -> str | None:
    if max_grade not in (10, 100):
        raise ValueError("Escolha a faixa de notas 0 a 10 ou 0 a 100.")
    text = str(value if value is not None else "").strip()
    if not text:
        return None
    if text.upper() in {"#VALUE!", "#VALOR!", "#REF!", "#N/A", "#N/D", "#DIV/0!", "#NAME?", "#NOME?", "#NUM!", "#NULL!", "#NULO!"}:
        raise ValueError(f"Erro de fórmula na planilha ({text}); corrija a célula antes do lançamento")
    try:
        number = Decimal(text.replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"Nota inválida: {text}") from exc
    if not number.is_finite() or number < 0 or number > max_grade:
        raise ValueError(f"Nota fora do intervalo 0 a {max_grade}: {text}")
    # Preservar a precisão original; não arredondar para uma casa.
    return format(number.normalize(), "f").replace(".", ",")


def suggest_grade_max(values) -> int:
    """Sugerir a faixa; nunca multiplicar ou dividir as notas."""
    for value in values:
        try:
            number = Decimal(str(value).strip().replace(",", "."))
        except InvalidOperation:
            continue
        if number.is_finite() and 10 < number <= 100:
            return 100
    return 10


SOPHIA_HEADERS = ["CodigoInstituicao", "CodigoPeriodoLetivo", "CodigoDisciplina", "CodigoTurma", "NomeTurma",
                 "CursoTurma", "CursoMatricula", "Disciplina", "RA", "CPF", "Nome", "Período", "Modalidade",
                 "Atividade", "Nota", "Conceito", "Faltoso", "Chamada", "CampusPolo", "NotaExportadaAcademico"]


def align_sophia_row(row: list[str], line: int, width: int) -> list[str]:
    """Realinhar somente a exportação SophiA conhecida, por âncoras únicas.

    Essa exportação não coloca aspas nas vírgulas de disciplinas, nomes e
    notas decimais. A largura constante não detecta o defeito: campos vazios
    no final compensam as vírgulas inseridas no meio da linha.
    """
    def invalid():
        raise ValueError(f"Exportação SophiA ambígua na linha {line}. Não foi possível alinhar os campos com segurança; exporte um XLSX ou um CSV com aspas.")

    def has_letters(value):
        return any(c.isalpha() for c in value)

    registrations = [i for i in range(8, len(row) - 3)
                     if re.fullmatch(r"\d{5,}", row[i].strip())
                     and (not row[i + 1].strip() or re.fullmatch(r"\d{1,11}", row[i + 1].strip()))
                     and has_letters(row[i + 2])]
    if len(registrations) != 1:
        invalid()
    registration = registrations[0]
    periods = [i for i in range(registration + 3, len(row) - 2)
               if re.fullmatch(r"\d{1,2}", row[i].strip())
               and re.fullmatch(r"[A-Za-z]{1,3}", row[i + 1].strip())
               and row[i + 2].strip()]
    if len(periods) != 1:
        invalid()
    period = periods[0]
    flags = [i for i in range(period + 3, len(row) - 3)
             if row[i].strip().lower() in {"true", "false"}
             and re.fullmatch(r"\d+", row[i + 1].strip())]
    if len(flags) != 1:
        invalid()
    flag = flags[0]
    payload = row[period + 3:flag]
    if len(payload) == 2:
        grade, concept = payload
    elif len(payload) == 3 and not payload[2].strip() and re.fullmatch(r"[+-]?\d+", payload[0].strip()) and re.fullmatch(r"\d+", payload[1].strip()):
        grade, concept = f"{payload[0].strip()},{payload[1].strip()}", payload[2]
        # Alinhamento estrutural não valida o intervalo da nota. Valores
        # fora de 0–10 devem chegar ao relatório como pendência da nota.
    else:
        invalid()
    if any(value.strip() for value in row[flag + 4:]):
        invalid()
    discipline = ", ".join(value.strip() for value in row[7:registration])
    name = ", ".join(value.strip() for value in row[registration + 2:period])
    aligned = [*row[:7], discipline, row[registration], row[registration + 1], name,
               *row[period:period + 3], grade, concept, *row[flag:flag + 4]]
    if len(aligned) != 20 or width < 20:
        invalid()
    return aligned + [""] * (width - 20)


def read_file(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise ValueError("O arquivo selecionado não existe.")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        raw_bytes = path.read_bytes()
        rows = None
        delimiter = ","
        for encoding in ("utf-8-sig", "cp1252", "latin1"):
            try:
                content = raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
            sample = content[:65536]
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
            except csv.Error:
                first_line = content.partition("\n")[0].rstrip("\r")
                delimiter = max(",;\t", key=lambda sep: len(next(csv.reader([first_line], delimiter=sep)))) if content.strip() else ","
            rows = list(csv.reader(io.StringIO(content), delimiter=delimiter))
            break
        if not rows or len(rows[0]) < 2:
            raise ValueError("CSV vazio ou sem colunas identificáveis.")
        headers = [str(h).strip() or f"Unnamed: {i}" for i, h in enumerate(rows[0])]
        if len(set(headers)) != len(headers):
            raise ValueError("Há cabeçalhos duplicados. Renomeie as colunas da planilha.")
        values = []
        sophia_export = delimiter == "," and [normalize(h) for h in headers[:20]] == [normalize(h) for h in SOPHIA_HEADERS]
        repaired = []
        expected_width = len(headers)
        for line, row in enumerate(rows[1:], 2):
            if not row or not any(row):
                continue
            if sophia_export:
                aligned = align_sophia_row(row, line, expected_width)
                if aligned != row:
                    repaired.append(line)
                row = aligned
            if len(row) != expected_width:
                raise ValueError(f"CSV com quantidade incorreta de campos na linha {line}; nenhuma linha será descartada silenciosamente.")
            values.append(row)
        if not values:
            raise ValueError("A planilha não contém registros.")
        frame = pd.DataFrame(values, columns=headers)
        frame.attrs["csv_normalized_rows"] = repaired
        return frame
    if suffix == ".xlsx":
        # pandas converte erros de fórmula do Excel para NaN mesmo com
        # keep_default_na=False. Preservar o erro para não chamá-lo de vazio.
        with path.open("rb") as source:
            book = load_workbook(source, read_only=True, data_only=True)
            try:
                sheet_name = next((s for s in book.sheetnames if any(k in normalize(s) for k in ("NOTA", "LANCAMENTO", "ALUNO", "RESPOSTA"))), book.sheetnames[0])
                rows = iter(book[sheet_name].iter_rows(values_only=True))
                first = next(rows, None)
                if first is None:
                    raise ValueError("A planilha não contém cabeçalhos.")
                columns = [str(c).strip() if c is not None else f"Unnamed: {i}" for i, c in enumerate(first)]
                if len(set(columns)) != len(columns):
                    raise ValueError("Há cabeçalhos duplicados. Renomeie as colunas da planilha.")
                width = len(columns)
                data_rows = []
                for row in rows:
                    converted = [str(value) if value is not None else "" for value in row[:width]]
                    if len(converted) < width:
                        converted.extend([""] * (width - len(converted)))
                    data_rows.append(converted)
                if not data_rows:
                    raise ValueError("A planilha não contém registros.")
                return pd.DataFrame(data_rows, columns=columns)
            finally:
                book.close()
    if suffix == ".xls":
        with pd.ExcelFile(path) as book:
            sheet = next((s for s in book.sheet_names if any(k in normalize(s) for k in ("NOTA", "LANCAMENTO", "ALUNO", "RESPOSTA"))), book.sheet_names[0])
            frame = pd.read_excel(book, sheet_name=sheet, dtype=str, keep_default_na=False)
            frame.columns = [str(c).strip() for c in frame.columns]
        if frame.empty:
            raise ValueError("A planilha não contém registros.")
        return frame.fillna("").astype(str)
    raise ValueError("Escolha um arquivo .csv, .xlsx ou .xls.")


def detect_column(columns, keywords) -> str:
    normalized_cols = [(col, normalize(col)) for col in columns]
    normalized_keys = [(key, normalize(key)) for key in keywords]
    for _, key_norm in normalized_keys:
        found = next((col for col, col_norm in normalized_cols if col_norm == key_norm), None)
        if found:
            return found
    for key, key_norm in normalized_keys:
        if len(key) > 2:
            found = next((col for col, col_norm in normalized_cols if key_norm in col_norm.replace("_", " ").split()), None)
            if found:
                return found
    return ""


@dataclass(frozen=True)
class Columns:
    name: str
    course: str
    discipline: str
    grade: str
    registration: str = ""
    unit: str = ""


@dataclass(frozen=True)
class Record:
    key: int
    line: int
    name: str
    course: str
    discipline: str
    raw_grade: str
    registration: str
    units: tuple[str, ...]


def records_from_frame(frame: pd.DataFrame, columns: Columns, courses: tuple[str, ...]) -> list[Record]:
    mapped = {"Nome": columns.name, "Curso": columns.course, "Disciplina": columns.discipline,
              "Nota": columns.grade, "RA": columns.registration, "Polo": columns.unit}
    seen = {}
    for label, column in mapped.items():
        if not column:
            continue
        if column in seen:
            raise ValueError(f"A coluna '{column}' foi escolhida para {seen[column]} e {label}. Confira o mapeamento na etapa 2; cada campo deve usar sua própria coluna.")
        seen[column] = label
    if normalize(columns.grade).replace(" ", "") in {"CAMPUSPOLO", "POLO", "UNIDADE", "CAMPUS"}:
        raise ValueError("O campo Nota está usando uma coluna de polo. Na etapa 2, selecione a coluna que contém as notas.")
    for col in (columns.name, columns.course, columns.discipline, columns.grade):
        if col not in frame.columns:
            raise ValueError("Selecione as colunas de nome, curso, disciplina e nota.")
    if not courses:
        raise ValueError("Selecione pelo menos um curso.")
    selected = {normalize(c) for c in courses}
    names = frame[columns.name].tolist()
    course_values = frame[columns.course].tolist()
    disciplines = frame[columns.discipline].tolist()
    grades = frame[columns.grade].tolist()
    registrations = frame[columns.registration].tolist() if columns.registration else None
    unit_values = frame[columns.unit].tolist() if columns.unit else None
    adjacent_values = None
    if columns.unit:
        position = frame.columns.get_loc(columns.unit)
        if isinstance(position, int) and position + 1 < len(frame.columns):
            adjacent_values = frame.iloc[:, position + 1].tolist()

    def clean_str(val) -> str:
        if isinstance(val, str):
            return val.strip()
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return ""
        return str(val).strip()

    result = []
    for idx, (name_val, course_val, disc_val, grade_val) in enumerate(zip(names, course_values, disciplines, grades)):
        if normalize(course_val) not in selected:
            continue
        candidates = []
        if unit_values is not None:
            value = unit_values[idx]
            if usable_unit(value):
                candidates.append(unit_name(value))
            elif adjacent_values is not None:
                # Exportação SophiA observada: CampusPolo contém Chamada e o
                # nome do polo foi deslocado uma coluna para a direita.
                adjacent = adjacent_values[idx]
                if usable_unit(adjacent):
                    candidates.append(unit_name(adjacent))
        reg = identifier(registrations[idx]) if registrations is not None else ""
        result.append(Record(idx, idx + 2, clean_str(name_val), clean_str(course_val),
                             clean_str(disc_val), clean_str(grade_val), reg, tuple(candidates)))
    if not result:
        raise ValueError("Não há registros para os cursos selecionados.")
    return result
