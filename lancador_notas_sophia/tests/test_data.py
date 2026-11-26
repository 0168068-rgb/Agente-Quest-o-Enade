import csv
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from openpyxl import Workbook, load_workbook

from sophia.data import Columns, SOPHIA_HEADERS, grade_value, identifier, read_file, records_from_frame, suggest_grade_max, unit_name
from sophia.report import write_report


class DataTests(unittest.TestCase):
    def test_unit_column_cannot_be_selected_as_grade(self):
        frame = pd.DataFrame([{"Nome": "Ana", "Curso": "Marketing", "Disciplina": "Branding", "Nota": "100", "CampusPolo": "Nova Iguaçu"}])
        for unit_column in ("CampusPolo", ""):
            with self.subTest(unit=unit_column), self.assertRaisesRegex(ValueError, "coluna"):
                records_from_frame(frame, Columns("Nome", "Curso", "Disciplina", "CampusPolo", unit=unit_column), ("Marketing",))

    def test_hundred_point_grades_are_preserved_without_division(self):
        for value in ("0", "5", "10", "70", "80", "90", "100", "99,75"):
            self.assertEqual(grade_value(value, max_grade=100), value)
        with self.assertRaises(ValueError):
            grade_value("100")
        with self.assertRaises(ValueError):
            grade_value("101", max_grade=100)
        with self.assertRaises(ValueError):
            grade_value("#VALUE!", max_grade=100)
        self.assertEqual(suggest_grade_max(["0", "9.5", ""]), 10)
        self.assertEqual(suggest_grade_max(["#VALUE!", "100", "70"]), 100)

    def test_unit_unicode_dashes_and_campus_prefix(self):
        for value in ("Nova Iguaçu", "Campus Nova Iguaçu – RJ", "Polo Nova Iguaçu — RJ", "Unidade Nova Iguaçu − RJ", "Campus Nova Iguaçu - RJ"):
            with self.subTest(value=value):
                self.assertEqual(unit_name(value), "NOVA IGUACU")
        self.assertNotEqual(unit_name("Itaperuna"), unit_name("Nova Iguaçu"))

    def test_excel_formula_error_is_preserved_instead_of_becoming_blank(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notas.xlsx"
            book = Workbook()
            book.active.append(["Nome", "Curso", "Disciplina", "Nota", "RA", "CampusPolo"])
            book.active.append(["Ana", "Marketing", "Branding", "#VALUE!", "001", "Campus Nova Iguaçu – RJ"])
            book.active.append(["Bia", "Marketing", "Branding", None, "002", "Nova Iguaçu"])
            book.save(path)
            book.close()
            frame = read_file(path)
            records = records_from_frame(frame, Columns("Nome", "Curso", "Disciplina", "Nota", "RA", "CampusPolo"), ("Marketing",))
            self.assertEqual(records[0].raw_grade, "#VALUE!")
            self.assertEqual(records[1].raw_grade, "")
            self.assertEqual(records[0].units, ("NOVA IGUACU",))
            with self.assertRaisesRegex(ValueError, "Erro de fórmula"):
                grade_value(records[0].raw_grade)

    def test_grades(self):
        self.assertEqual(grade_value(0), "0")
        self.assertEqual(grade_value("8.125"), "8,125")
        self.assertEqual(grade_value("10,000"), "10")
        self.assertIsNone(grade_value(""))
        for bad in ("nan", "infinity", "Prova", "-1", "11", "1,2,3"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                grade_value(bad)

    def test_exact_registration(self):
        self.assertEqual(identifier("00123"), "00123")
        self.assertEqual(identifier("123.0"), "123")
        self.assertNotEqual(identifier("00123"), identifier("123"))

    def test_csv_and_shifted_unit_and_multiple_courses(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notas.csv"
            path.write_text("Nome;Curso;Disciplina;Nota;RA;CampusPolo;NotaExportadaAcademico\nAna;Fisioterapia;Anatomia;0;001;1;Nova Iguaçu\nBia;Computação;Redes;8,125;002;Itaperuna;Nota não exportada\nCaio;Outro;X;3;003;Outro;\n", encoding="utf-8-sig")
            frame = read_file(path)
            cols = Columns("Nome", "Curso", "Disciplina", "Nota", "RA", "CampusPolo")
            rows = records_from_frame(frame, cols, ("Fisioterapia", "Computação"))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0].units, ("NOVA IGUACU",))
            self.assertEqual(rows[0].registration, "001")
            self.assertEqual(rows[1].units, ("ITAPERUNA",))
            self.assertEqual(rows[1].raw_grade, "8,125")

    def test_bad_files_and_no_silent_skips(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notas.csv"
            for content in ("", "Nome;Nota\nAna;8;campo_extra\n", "Nome;Nome\nAna;Bia\n"):
                path.write_text(content, encoding="utf-8")
                with self.subTest(content=content), self.assertRaises(ValueError):
                    read_file(path)
            with self.assertRaises(ValueError):
                read_file(Path(directory) / "inexistente.xlsx")

    def test_excel_and_mapping_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notas.xlsx"
            book = Workbook()
            book.active.title = "Notas"
            book.active.append(["Nome", "Curso", "Disciplina", "Nota", "RA"])
            book.active.append(["Ana", "Fisioterapia", "Anatomia", 0, "0001"])
            book.save(path)
            book.close()
            rows = records_from_frame(read_file(path), Columns("Nome", "Curso", "Disciplina", "Nota", "RA"), ("Fisioterapia",))
            self.assertEqual(rows[0].raw_grade, "0")
            self.assertEqual(rows[0].registration, "0001")
            with self.assertRaises(ValueError):
                records_from_frame(read_file(path), Columns("NãoExiste", "Curso", "Disciplina", "Nota"), ("Fisioterapia",))

    def test_report_three_sheets_no_formulas_and_unique_names(self):
        with tempfile.TemporaryDirectory() as directory:
            row = {"Aluno": "=2+2", "RA": "001", "Nota": "0", "Status / Motivo": "Simulação"}
            first = write_report(Path(directory), [row], [], [], False)
            second = write_report(Path(directory), [], [], [], True)
            self.assertNotEqual(first, second)
            book = load_workbook(first)
            try:
                self.assertEqual(book.sheetnames, ["Resultados", "Planilha - Pendentes", "Web - Sem Planilha"])
                self.assertNotEqual(book["Resultados"]["B2"].data_type, "f")
                self.assertEqual(book["Resultados"]["C2"].value, "001")
                self.assertEqual(book["Resultados"]["J2"].value, 0)
                self.assertEqual(book["Resultados"]["J2"].data_type, "n")
                self.assertEqual(book["Resultados"].freeze_panes, "A2")
            finally:
                book.close()

    def test_sophia_unquoted_commas_align_name_ra_grade_and_unit(self):
        row = ["39", "20262_G", "21", "T", "Graduação", "Graduação EAD", "Redes",
               "Qualidade, Segurança, Meio Ambiente e Saúde - QSMS", "721012345", "12345678901",
               "Pessoa de Teste", "1", "D", "Prova (1º chamada)", "8,5", "", "false", "1",
               "Nova Iguaçu", "Nota não exportada"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notas.csv"
            # Cabeçalho e linha têm 23 campos: validar a largura não detecta o erro.
            content = ",".join(SOPHIA_HEADERS + ["", "", ""]) + "\n" + ",".join(row) + "\n"
            self.assertEqual(len(list(csv.reader(content.splitlines()))[1]), 23)
            path.write_text(content, encoding="utf-8-sig")
            frame = read_file(path)
            actual = frame.iloc[0]
            self.assertEqual(actual.Nome, "Pessoa de Teste")
            self.assertEqual(actual.RA, "721012345")
            self.assertEqual(actual.Disciplina, row[7])
            self.assertEqual(actual.Nota, "8,5")
            self.assertEqual(actual.CampusPolo, "Nova Iguaçu")
            self.assertEqual(frame.attrs["csv_normalized_rows"], [2])

    def test_sophia_names_with_commas_and_quoted_exports(self):
        row = ["39", "20262_G", "21", "T", "Graduação", "Graduação EAD", "Redes",
               "Qualidade, Segurança", "721012345", "12345678901", "Pessoa, de Teste",
               "1", "D", "Prova (1º chamada)", "9,75", "", "false", "1", "Nova Iguaçu", "Nota não exportada"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notas.csv"
            for quoted in (True, False):
                with path.open("w", encoding="utf-8-sig", newline="") as stream:
                    if quoted:
                        writer = csv.writer(stream)
                        writer.writerow(SOPHIA_HEADERS)
                        writer.writerow(row)
                    else:
                        stream.write(",".join(SOPHIA_HEADERS) + "\n" + ",".join(row) + "\n")
                frame = read_file(path)
                self.assertEqual(frame.iloc[0].Nome, "Pessoa, de Teste")
                self.assertEqual(frame.iloc[0].Nota, "9,75")

    def test_ambiguous_sophia_row_is_rejected_instead_of_guessing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notas.csv"
            path.write_text(",".join(SOPHIA_HEADERS) + "\n" + ",".join(["campo"] * 20), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ambígua na linha 2"):
                read_file(path)

    def test_sophia_out_of_range_grade_remains_a_grade_validation_issue(self):
        row = ["39", "20262_G", "21", "T", "Graduação", "Graduação EAD", "Redes", "Disciplina",
               "721012345", "12345678901", "Pessoa de Teste", "1", "D", "Prova", "11,0", "",
               "false", "1", "Nova Iguaçu", "Nota não exportada"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notas.csv"
            path.write_text(",".join(SOPHIA_HEADERS) + "\n" + ",".join(row), encoding="utf-8")
            frame = read_file(path)
            self.assertEqual(frame.iloc[0].Nota, "11,0")
            with self.assertRaisesRegex(ValueError, "fora do intervalo"):
                grade_value(frame.iloc[0].Nota)


if __name__ == "__main__":
    unittest.main()
