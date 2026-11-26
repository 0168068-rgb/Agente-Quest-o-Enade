import asyncio
import tempfile
import threading
import unittest
from pathlib import Path

from sophia.data import Record
from sophia.engine import RunConfig, run
from sophia.portal import BrowserPortal, Cancelled, GRID_SCRIPT, Option, PortalDialogBlocked


class LocalPortal(BrowserPortal):
    """Intercepta todo HTTP: não acessa o SophiA nem qualquer site externo."""
    async def open(self):
        from playwright.async_api import async_playwright
        self.manager = async_playwright()
        self.playwright = await self.manager.start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        context = await self.browser.new_context()
        fixture = Path(__file__).with_name("portal_fixture.html").read_text(encoding="utf-8")
        await context.route("**/*", lambda route: route.fulfill(status=200, body=fixture, content_type="text/html"))
        self.page = await context.new_page()
        self.page.set_default_timeout(3000)
        async def handler(dialog):
            await dialog.accept() if self.saving else await dialog.dismiss()
        self.page.on("dialog", handler)
        await self.page.goto("http://127.0.0.1/LancNotas.aspx")
        if getattr(self, "fail_save", False):
            await self.page.evaluate("window.failSave=true")
        if getattr(self, "missing_exam", False):
            await self.page.evaluate("window.missingAD=true")

    async def settle(self, cancellable=True):
        # Fixture síncrona; não precisa esperar por postbacks reais.
        if cancellable:
            self.check()
        await self.page.wait_for_function("!window.Sys.WebForms.PageRequestManager.getInstance().get_isInAsyncPostBack()")

    async def close(self):
        if self.page and not self.page.is_closed():
            self.observed = await self.page.evaluate("({saved:window.saved,saves:window.saves,searches:window.searches})")
        await super().close()


class BrowserTests(unittest.IsolatedAsyncioTestCase):
    async def make_modal(self, portal):
        await portal.page.evaluate("""() => {
            const overlay=document.createElement('div');overlay.className='cortinaDialogo';
            overlay.style='position:fixed;inset:0;background:#8888;z-index:1000';
            const dialog=document.createElement('div');dialog.setAttribute('role','dialog');
            dialog.style='position:fixed;top:100px;left:100px;background:white;z-index:1001;padding:20px';
            dialog.innerHTML='<p>Mensagem fictícia do portal</p><button>Fechar diálogo de teste</button>';
            dialog.querySelector('button').onclick=()=>{overlay.remove();dialog.remove()};
            document.body.append(overlay,dialog);
        }""")

    async def test_html_modal_waits_for_manual_dismissal_and_saves_image(self):
        messages = []
        portal = LocalPortal(threading.Event(), messages.append)
        with tempfile.TemporaryDirectory() as directory:
            portal.diagnostic_folder = Path(directory)
            try:
                await portal.open()
                await self.make_modal(portal)
                waiter = asyncio.create_task(portal.wait_for_portal_dialog())
                for _ in range(200):
                    if any("Aguardando a janela" in e["message"] for e in messages):
                        break
                    await asyncio.sleep(0.01)
                self.assertFalse(waiter.done())
                self.assertTrue(any("Mensagem fictícia" in e["message"] for e in messages))
                await portal.page.get_by_role("button", name="Fechar diálogo de teste").click()
                await asyncio.wait_for(waiter, 3)
                self.assertEqual(len(list(Path(directory).glob("janela_sophia_*.png"))), 1)
                self.assertEqual((await portal.page.evaluate("window.saves")), 0)
            finally:
                await portal.close()

    async def test_html_modal_timeout_does_not_force_click_or_claim_success(self):
        portal = LocalPortal(threading.Event(), lambda _: None)
        portal.dialog_timeout = 0.05
        try:
            await portal.open()
            await self.make_modal(portal)
            with self.assertRaisesRegex(PortalDialogBlocked, "Mensagem fictícia"):
                await portal.wait_for_portal_dialog()
            self.assertEqual(await portal.page.locator('.cortinaDialogo:visible').count(), 1)
        finally:
            await portal.close()

    async def test_html_modal_can_be_cancelled_with_uncertain_result(self):
        cancellation = threading.Event()
        portal = LocalPortal(cancellation, lambda _: None)
        try:
            await portal.open()
            await self.make_modal(portal)
            cancellation.set()
            with self.assertRaises(Cancelled):
                await portal.wait_for_portal_dialog()
        finally:
            await portal.close()

    async def test_html_modal_auto_confirms_save_success_dialog(self):
        messages = []
        portal = LocalPortal(threading.Event(), messages.append)
        try:
            await portal.open()
            await portal.page.evaluate("""() => {
                const overlay=document.createElement('div');overlay.className='cortinaDialogo';
                overlay.style='position:fixed;inset:0;background:#8888;z-index:1000';
                const dialog=document.createElement('div');dialog.setAttribute('role','dialog');
                dialog.style='position:fixed;top:100px;left:100px;background:white;z-index:1001;padding:20px';
                dialog.innerHTML='<p>As informações foram salvas com sucesso. Entretanto, existem avaliações em que os lançamentos não foram concluídos.</p><input type="button" value="Confirmar">';
                dialog.querySelector('input').onclick=()=>{overlay.remove();dialog.remove()};
                document.body.append(overlay,dialog);
            }""")
            await asyncio.wait_for(portal.wait_for_portal_dialog(), 3)
            self.assertEqual(await portal.page.locator('.cortinaDialogo:visible').count(), 0)
            self.assertTrue(any("fechada automaticamente" in e["message"] for e in messages))
        finally:
            await portal.close()

    async def execute(self, simulation=True, fail_save=False, missing_exam=False, grade_max=10, first_grade="0", second_grade="8.125"):
        with tempfile.TemporaryDirectory() as directory:
            cancel = threading.Event()
            portal = LocalPortal(cancel, lambda _: None)
            portal.fail_save = fail_save
            portal.missing_exam = missing_exam
            records = [Record(0, 2, "Ana", "Fisioterapia", "Anatomia", first_grade, "001", ("ITAPERUNA",)),
                       Record(1, 3, "Bia", "Fisioterapia", "Anatomia", second_grade, "002", ("NOVA IGUACU",))]
            config = RunConfig("2026.2", "AD", ("Fisioterapia",), simulation, Path(directory), grade_max=grade_max)
            result = await run(config, records, cancel, lambda _: None, portal)
            self.assertFalse(result.partial, result.error)
            return result, portal.observed

    async def test_browser_simulation_no_save_and_restores_nova_iguacu(self):
        result, observed = await self.execute()
        self.assertEqual(len(result.results), 2)
        self.assertEqual(observed["saves"], 0)
        self.assertEqual(observed["saved"], {})
        self.assertEqual({s["unit"] for s in observed["searches"]}, {"i", "n"})
        self.assertTrue(all(s["period"] == "43" for s in observed["searches"]))

    async def test_browser_real_reloads_correct_cell_and_keeps_ai(self):
        result, observed = await self.execute(False)
        self.assertEqual(len(result.results), 2)
        self.assertEqual(observed["saves"], 2)
        self.assertEqual(observed["saved"]["001"], "0")
        self.assertEqual(observed["saved"]["002"], "8,125")
        self.assertEqual(observed["saved"]["ai-001"], "6")
        self.assertEqual(observed["saved"]["ai-002"], "6")

    async def test_browser_hundred_point_notes_remain_100_and_90(self):
        result, observed = await self.execute(False, grade_max=100, first_grade="100", second_grade="90")
        self.assertEqual(len(result.results), 2)
        self.assertEqual(observed["saved"]["001"], "100")
        self.assertEqual(observed["saved"]["002"], "90")
        self.assertEqual(observed["saved"]["ai-001"], "6")

    async def test_browser_failed_save_does_not_report_success(self):
        result, observed = await self.execute(False, fail_save=True)
        self.assertEqual(len(result.results), 0)
        self.assertEqual(len(result.pending), 2)
        self.assertEqual(observed["saves"], 2)

    async def test_browser_missing_ad_never_fills_md_or_saves(self):
        result, observed = await self.execute(False, missing_exam=True)
        self.assertEqual(len(result.results), 0)
        self.assertEqual(len(result.pending), 2)
        self.assertEqual(observed["saves"], 0)

    async def test_real_settle_waits_for_delayed_webforms_postback(self):
        portal = LocalPortal(threading.Event(), lambda _: None)
        try:
            await portal.open()
            await portal.page.evaluate("busy=true;setTimeout(()=>{busy=false;periodChanged()},600)")
            await BrowserPortal.settle(portal)
            self.assertEqual(len(await portal.options("unidade")), 2)
        finally:
            await portal.close()


if __name__ == "__main__":
    unittest.main()
