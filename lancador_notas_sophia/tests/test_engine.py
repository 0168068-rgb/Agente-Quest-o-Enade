import tempfile
import threading
import unittest
from pathlib import Path

from sophia.data import Record, unit_name
from sophia.engine import RunConfig, run
from sophia.portal import Cancelled, Option, PortalDialogBlocked, Student


class FakePortal:
    def __init__(self, cancellation):
        self.cancel = cancellation
        self.unit = None
        self.current = {}
        self.saved = {}
        self.save_calls = 0
        self.fill_calls = 0
        self.closed = False
        self.fail_save = False
        self.fail_fill_at = None
        self.cancel_after_fill = False
        self.cancel_after_save = False
        self.fail_inventory = False
        self.missing_exam = False
        self.multiple_stages = False

    async def open(self):
        pass

    async def close(self):
        self.closed = True

    async def select(self, kind, option):
        if kind == "periodo":
            self.period = option

    async def restore(self, period, unit=None, classroom=None, stage=None, discipline=None):
        self.period = period
        self.unit = unit
        self.stage = stage
        self.current = dict(self.saved)
        if self.fail_inventory and unit and unit.value == "n":
            raise RuntimeError("Falha de rede durante inventário")

    async def options(self, kind):
        if kind == "periodo":
            return [Option("43", "2026.2")]
        if kind == "unidade":
            return [Option("i", "Itaperuna"), Option("n", "Nova Iguaçu")]
        if kind == "turma":
            return [Option("t", "G - Fisioterapia")]
        if kind == "etapa":
            return [Option("s", "Semestre"), Option("e", "Outra etapa")] if self.multiple_stages else [Option("s", "Semestre")]
        return [Option("a", "Anatomia")]

    async def search(self):
        pass

    async def roster(self, exam):
        code = "001" if self.unit.value == "i" else "002"
        name = "Ana" if self.unit.value == "i" else "Bia"
        available = not self.multiple_stages or self.stage.value == "e"
        return not self.missing_exam, [Student(code, name, code, code if not self.missing_exam and available else None, self.current.get(code, "")),
                                       Student("extra", "Aluno Extra", "999", "extra", "")]

    async def fill(self, student, value):
        if self.cancel.is_set():
            raise Cancelled("Cancelado")
        self.fill_calls += 1
        if self.fail_fill_at == self.fill_calls:
            raise RuntimeError("Campo não aceitou o preenchimento")
        self.current[student.key] = value
        if self.cancel_after_fill:
            self.cancel.set()

    async def save_and_reload(self, task, exam):
        self.save_calls += 1
        if not self.fail_save:
            self.saved = dict(self.current)
        self.current = dict(self.saved)
        if self.cancel_after_save:
            self.cancel.set()
        return (await self.roster(exam))[1]


class EngineTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.cancel = threading.Event()
        self.portal = FakePortal(self.cancel)
        self.records = [Record(0, 2, "Ana", "Fisioterapia", "Anatomia", "0", "001", ("ITAPERUNA",)),
                        Record(1, 3, "Bia", "Fisioterapia", "Anatomia", "8.125", "002", ("NOVA IGUACU",)),
                        Record(2, 4, "Caio", "Fisioterapia", "Disciplina ausente", "7", "003", ("NOVA IGUACU",))]

    def tearDown(self):
        self.folder.cleanup()

    async def execute(self, simulation=True, period="2026.2", grade_max=10):
        config = RunConfig(period, "AD", ("Fisioterapia",), simulation, Path(self.folder.name), grade_max=grade_max)
        return await run(config, self.records, self.cancel, lambda _: None, self.portal)

    async def test_simulation_never_saves_and_omits_only_unavailable(self):
        result = await self.execute()
        self.assertEqual(len(result.results), 2)
        self.assertEqual(result.omitted, 1)
        self.assertEqual(self.portal.save_calls, 0)
        self.assertTrue(all("não gravado" in r["Status / Motivo"] for r in result.results))
        self.assertEqual(len(result.absent), 2)
        self.assertTrue(self.portal.closed)

    async def test_hundred_point_scale_simulation_preserves_100_and_does_not_save(self):
        self.records[1] = Record(1, 3, "Bia", "Fisioterapia", "Anatomia", "100", "002", ("NOVA IGUACU",))
        result = await self.execute(grade_max=100)
        self.assertEqual(len(result.results), 2)
        self.assertEqual(result.results[1]["Nota"], "100")
        self.assertEqual(self.portal.current["002"], "100")
        self.assertEqual(self.portal.save_calls, 0)

    async def test_hundred_point_scale_is_verified_after_real_mock_save(self):
        self.records[1] = Record(1, 3, "Bia", "Fisioterapia", "Anatomia", "90", "002", ("NOVA IGUACU",))
        result = await self.execute(False, grade_max=100)
        self.assertEqual(len(result.results), 2)
        self.assertEqual(self.portal.saved["002"], "90")


    async def test_real_save_reloaded_and_confirmed(self):
        result = await self.execute(False)
        self.assertEqual(self.portal.save_calls, 2)
        self.assertEqual(len(result.results), 2)
        self.assertEqual(self.portal.saved["002"], "8,125")
        self.assertTrue(all("releitura" in row["Status / Motivo"] for row in result.results))

    async def test_unconfirmed_saves_are_pending(self):
        self.portal.fail_save = True
        result = await self.execute(False)
        self.assertEqual(len(result.results), 0)
        self.assertEqual(len(result.pending), 2)
        self.assertTrue(all("não confirmada" in r["Status / Motivo"] for r in result.pending))

    async def test_blocking_dialog_stops_run_and_retains_uncertain_save(self):
        async def blocked_save(task, exam):
            self.portal.save_calls += 1
            raise PortalDialogBlocked("Janela aberta: mensagem de validação")
        self.portal.save_and_reload = blocked_save
        result = await self.execute(False)
        self.assertTrue(result.partial)
        self.assertEqual(self.portal.save_calls, 1)
        self.assertEqual(len(result.results), 0)
        self.assertTrue(any("Gravação não confirmada" in r["Status / Motivo"] for r in result.pending))

    async def test_cancel_before_login_creates_partial_all_rows(self):
        self.cancel.set()
        result = await self.execute()
        self.assertTrue(result.partial)
        self.assertEqual(len(result.pending), 3)
        self.assertEqual(result.omitted, 0)
        self.assertTrue(result.path.exists())
        self.assertEqual(self.portal.fill_calls, 0)

    async def test_cancel_after_filling_does_not_save(self):
        self.portal.cancel_after_fill = True
        result = await self.execute(False)
        self.assertTrue(result.partial)
        self.assertEqual(self.portal.save_calls, 0)
        self.assertEqual(len(result.results) + len(result.pending) + result.omitted, 3)

    async def test_cancel_after_saving_keeps_confirmed_result(self):
        self.portal.cancel_after_save = True
        result = await self.execute(False)
        self.assertTrue(result.partial)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(self.portal.save_calls, 1)

    async def test_missing_period_stops_without_filling(self):
        result = await self.execute(period="2026.1")
        self.assertTrue(result.partial)
        self.assertIn("indisponível", result.error)
        self.assertEqual(self.portal.fill_calls, 0)

    async def test_failed_inventory_does_not_silently_omit(self):
        self.portal.fail_inventory = True
        result = await self.execute()
        self.assertTrue(result.partial)
        self.assertEqual(len(result.pending), 3)
        self.assertEqual(result.omitted, 0)

    async def test_exact_ra_does_not_fall_back_to_similar_name(self):
        self.records[0] = Record(0, 2, "Ana", "Fisioterapia", "Anatomia", "9", "01", ("ITAPERUNA",))
        result = await self.execute()
        self.assertEqual(len(result.pending), 1)
        self.assertIn("não localizado", result.pending[0]["Status / Motivo"])

    async def test_duplicates_and_missing_grades(self):
        self.records.append(Record(3, 5, "Ana", "Fisioterapia", "Anatomia", "9", "001", ("ITAPERUNA",)))
        self.records[1] = Record(1, 3, "Bia", "Fisioterapia", "Anatomia", "", "002", ("NOVA IGUACU",))
        result = await self.execute()
        self.assertEqual(len(result.pending), 3)
        self.assertEqual(len(result.results), 0)
        self.assertEqual(self.portal.fill_calls, 0)

    async def test_missing_exam_never_fills_other_field(self):
        self.portal.missing_exam = True
        result = await self.execute()
        self.assertEqual(len(result.pending), 2)
        self.assertEqual(self.portal.fill_calls, 0)

    async def test_available_only_in_another_stage(self):
        self.portal.multiple_stages = True
        result = await self.execute()
        self.assertEqual(len(result.results), 2)
        self.assertTrue(all(r["Etapa"] == "Outra etapa" for r in result.results))

    async def test_unknown_unit_is_pending_not_omitted(self):
        self.records[0] = Record(0, 2, "Ana", "Fisioterapia", "Anatomia", "9", "001", ())
        result = await self.execute()
        self.assertEqual(len(result.pending), 1)
        self.assertIn("Polo", result.pending[0]["Status / Motivo"])

    async def test_campus_unicode_dash_matches_portal_unit(self):
        self.records[1] = Record(1, 3, "Bia", "Fisioterapia", "Anatomia", "8", "002", (unit_name("Campus Nova Iguaçu – RJ"),))
        result = await self.execute()
        self.assertEqual(len(result.results), 2)
        self.assertEqual(len(result.pending), 0)
        self.assertEqual(self.portal.save_calls, 0)

    async def test_excel_error_is_not_reported_as_missing_grade(self):
        self.records[1] = Record(1, 3, "Bia", "Fisioterapia", "Anatomia", "#VALUE!", "002", ("NOVA IGUACU",))
        result = await self.execute()
        self.assertEqual(len(result.pending), 1)
        self.assertIn("Erro de fórmula", result.pending[0]["Status / Motivo"])
        self.assertEqual(self.portal.save_calls, 0)

    async def test_unit_specific_unavailable_discipline_is_omitted(self):
        original = self.portal.options
        async def options(kind):
            if kind == "disciplina" and self.portal.unit.value == "n":
                return [Option("other", "Outra disciplina")]
            return await original(kind)
        self.portal.options = options
        result = await self.execute()
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.omitted, 2)
        self.assertEqual(len(result.pending), 0)

    async def test_fill_failure_prevents_saving_partially_modified_batch(self):
        original = self.portal.roster
        async def roster(exam):
            header, students = await original(exam)
            if self.portal.unit.value == "i":
                students.append(Student("004", "Dora", "004", "004", ""))
            return header, students
        self.portal.roster = roster
        self.records.append(Record(3, 5, "Dora", "Fisioterapia", "Anatomia", "9", "004", ("ITAPERUNA",)))
        self.portal.fail_fill_at = 2
        result = await self.execute(False)
        self.assertEqual(self.portal.save_calls, 1)  # Somente o lote Nova Iguaçu.
        self.assertEqual(len(result.results), 1)
        self.assertEqual(len(result.pending), 2)
        self.assertNotIn("001", self.portal.saved)


if __name__ == "__main__":
    unittest.main()
