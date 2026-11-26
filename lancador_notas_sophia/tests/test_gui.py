import os
import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from sophia.engine import RunResult
from sophia.gui import Application, STAGE_HELP


@unittest.skipUnless(os.name == "nt" or os.environ.get("DISPLAY"), "Requer ambiente gráfico")
class GuiTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = Application(self.root)
        self.directory = tempfile.TemporaryDirectory()
        self.app.folder.set(self.directory.name)
        frame = pd.DataFrame([{"Nome": "Ana", "Curso": "Fisioterapia", "Disciplina": "Anatomia", "Nota": "0", "RA": "001", "CampusPolo": "Itaperuna"}])
        self.app.events.put(("loaded", "notas.csv", frame))
        self.app.poll()
        self.app.course_list.selection_set(0)

    def tearDown(self):
        self.app.progress.stop()
        for callback in self.root.tk.call("after", "info"):
            self.root.after_cancel(callback)
        self.root.destroy()
        self.directory.cleanup()

    def test_default_simulation_mapping_and_worker_delivery(self):
        self.assertEqual(self.app.mode.get(), "simulacao")
        self.assertEqual(self.app.columns["grade"].get(), "Nota")
        calls = []
        async def fake_run(config, records, cancellation, emit):
            calls.append((config, records))
            emit({"message": "Teste local", "current": 1, "total": 1})
            return RunResult(Path(self.directory.name) / "teste.xlsx", [], [], [], 0, False)
        with patch("sophia.engine.run", fake_run):
            self.app.start()
            deadline = time.monotonic() + 3
            while self.app.busy and time.monotonic() < deadline:
                self.root.update()
                time.sleep(0.01)
            self.assertFalse(self.app.busy)
        self.assertTrue(calls[0][0].simulation)
        self.assertEqual(calls[0][1][0].raw_grade, "0")
        self.assertIsNotNone(self.app.last_report)

    def test_real_mode_requires_confirmation(self):
        self.app.mode.set("real")
        with patch("sophia.gui.messagebox.askyesno", return_value=False) as confirm, patch("sophia.engine.run") as runner:
            self.app.start()
            confirm.assert_called_once()
            runner.assert_not_called()
            self.assertFalse(self.app.busy)

    def test_grade_mapped_to_unit_is_blocked_before_opening_browser(self):
        self.app.columns['grade'].set('CampusPolo')
        with patch('sophia.gui.messagebox.showerror') as error, patch('sophia.engine.run') as runner:
            self.app.start()
            error.assert_called_once()
            runner.assert_not_called()
            self.assertEqual(self.app.active_stage, 2)

    def test_mouse_wheel_does_not_change_selected_grade_column(self):
        before = self.app.columns['grade'].get()
        self.app.combos['grade'].event_generate('<MouseWheel>', delta=-120)
        self.app.combos['grade'].event_generate('<Button-5>')
        self.assertEqual(self.app.columns['grade'].get(), before)

    def test_cancel_sets_event_without_closing_worker(self):
        self.app.busy_state(True)
        self.app.cancel()
        self.assertTrue(self.app.cancel_event.is_set())
        self.assertTrue(self.app.busy)

    def test_loaded_courses_are_populated_while_controls_disabled(self):
        frame = pd.DataFrame([{"Nome": "Ana", "CursoMatricula": "Análise e Desenvolvimento de Sistemas", "Disciplina": "Redes", "Nota": "8"}])
        self.app.busy_state(True)
        self.app.events.put(("loaded", "nova.csv", frame))
        self.app.poll()
        self.assertEqual(self.app.course_list.size(), 1)
        self.assertEqual(self.app.course_list.get(0), "Análise e Desenvolvimento de Sistemas")
        self.assertEqual(self.app.course_list.cget("state"), "normal")
        self.app.course_list.selection_set(0)
        self.assertEqual(self.app.course_list.curselection(), (0,))

    def test_stage_guidance_initial_and_after_loading(self):
        self.assertEqual(self.app.active_stage, 2)
        self.assertIn("Confira as colunas", self.app.guide.get())
        self.app.show_stage(1)
        self.assertEqual(self.app.guide.get(), STAGE_HELP[1])
        self.app.show_stage(3)
        self.assertIn("Disponíveis: 1. Selecionados: 1.", self.app.guide.get())
        self.app.select_courses(False)
        self.assertIn("Selecionados: 0.", self.app.guide.get())

    def test_loaded_hundred_point_notes_suggest_range_without_changing_values(self):
        frame = pd.DataFrame([{"Nome": "Ana", "Curso": "Marketing", "Disciplina": "Branding", "Nota": "100"}])
        self.app.events.put(("loaded", "notas.xlsx", frame))
        self.app.poll()
        self.assertEqual(self.app.grade_range.get(), "0 a 100")
        self.assertEqual(self.app.frame.iloc[0]["Nota"], "100")
        self.assertEqual(self.app.mode.get(), "simulacao")

    def test_field_focus_updates_guidance_and_busy_keeps_processing_stage(self):
        self.app.combos["grade"].event_generate("<FocusIn>")
        self.assertEqual(self.app.active_stage, 2)
        self.app.period_combo.event_generate("<FocusIn>")
        self.assertEqual(self.app.active_stage, 4)
        self.assertIn("sem gravar", self.app.guide.get())
        self.app.busy_state(True)
        self.app.show_stage(6, force=True)
        self.app.show_stage(3)
        self.assertEqual(self.app.active_stage, 6)

    def test_small_window_has_scrollable_steps_and_fixed_actions(self):
        self.root.deiconify()
        self.root.geometry("860x650")
        self.root.update()
        self.assertGreater(self.app.body.winfo_height(), self.app.canvas.winfo_height())
        self.app.show_stage(6)
        self.root.update()
        self.assertGreater(self.app.canvas.yview()[0], 0)
        button = self.app.start_button
        self.assertLess(button.winfo_rooty() + button.winfo_height(), self.root.winfo_rooty() + self.root.winfo_height())
        self.assertTrue(button.winfo_ismapped())

    def test_rounded_borders_cover_full_groups_and_do_not_overlap_titles(self):
        self.root.deiconify()
        self.root.update()
        for group in self.app.sections.values():
            self.assertEqual(group.backdrop.winfo_x(), 0)
            self.assertEqual(group.backdrop.winfo_y(), 0)
            self.assertEqual(group.backdrop.winfo_width(), group.winfo_width())
            self.assertEqual(group.backdrop.winfo_height(), group.winfo_height())
            self.assertLessEqual(group.title_label.winfo_y() + group.title_label.winfo_height(), 36)
        for field in self.app.combos.values():
            self.assertEqual(field.backdrop.winfo_width(), field.winfo_width())
            self.assertEqual(field.backdrop.winfo_height(), field.winfo_height())
            self.assertGreater(field.field.winfo_y(), 0)


if __name__ == "__main__":
    unittest.main()
