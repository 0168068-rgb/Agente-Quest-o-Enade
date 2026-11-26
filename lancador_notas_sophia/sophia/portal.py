from __future__ import annotations

import asyncio
import os
import sys
import time
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import async_playwright

from .data import normalize

SOPHIA_URL = "https://portal.sophia.com.br/SophiA_111/Acesso.aspx?escola=8262"


class Cancelled(Exception):
    pass


class PortalDialogBlocked(RuntimeError):
    """Uma janela do portal impede confirmar o resultado da operação."""
    pass


@dataclass(frozen=True)
class Option:
    value: str
    text: str


@dataclass(frozen=True)
class Task:
    period: Option
    unit: Option
    classroom: Option
    stage: Option
    discipline: Option


@dataclass(frozen=True)
class Student:
    key: str
    name: str
    registration: str
    input_selector: str | None
    value: str


# Escolher a célula da avaliação pelo cabeçalho; nunca pelo índice na
# lista de inputs. Não há fallback para a primeira coluna de notas.
GRID_SCRIPT = r"""(exam) => {
    const norm = value => (value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().replace(/\s+/g, ' ').trim();
    const tables = Array.from(document.querySelectorAll('table'));
    for (const table of tables) {
        const rows = Array.from(table.rows).filter(row => row.closest('table') === table);
        for (let h = 0; h < rows.length; h++) {
            const headers = Array.from(rows[h].cells).map(cell => norm(cell.innerText));
            const nameIndex = headers.findIndex(v => v === 'NOME' || v === 'ALUNO' || v === 'NOME DO ALUNO');
            const codeIndex = headers.findIndex(v => ['CODIGO', 'CODIGO DO ALUNO', 'RA', 'MATRICULA'].includes(v));
            if (nameIndex < 0 || codeIndex < 0) continue;
            const gradeIndexes = headers.map((v, i) => v.split(/[^A-Z0-9]+/).includes(exam) ? i : -1).filter(i => i >= 0);
            const gradeIndex = gradeIndexes.length === 1 ? gradeIndexes[0] : -1;
            const students = [];
            for (let i = h + 1; i < rows.length; i++) {
                const cells = Array.from(rows[i].cells);
                if (!cells[nameIndex] || !cells[codeIndex] || cells[nameIndex].tagName === 'TH') continue;
                const nameCell = cells[nameIndex];
                const name = nameCell.getAttribute('title') || nameCell.querySelector('[title]')?.getAttribute('title') || nameCell.innerText.trim();
                const registration = cells[codeIndex].innerText.trim();
                if (!name || !registration) continue;
                const gradeCell = gradeIndex >= 0 ? cells[gradeIndex] : null;
                const inputs = gradeCell ? Array.from(gradeCell.querySelectorAll('input[type="text"], input[type="number"], input:not([type])')) : [];
                const input = inputs.length === 1 ? inputs[0] : null;
                let selector = null;
                if (input && !input.disabled && !input.readOnly) {
                    const tag = 'student-' + i;
                    input.setAttribute('data-sophia-grade', tag);
                    selector = '[data-sophia-grade="' + tag + '"]';
                }
                students.push({key: String(i), name, registration, input_selector: selector,
                               value: input ? input.value : (gradeCell?.innerText.trim() || '')});
            }
            return {header_found: gradeIndex >= 0, students};
        }
    }
    return {header_found: false, students: []};
}"""


class BrowserPortal:
    def __init__(self, cancel_event, emit, *, headless=False, url=SOPHIA_URL, diagnostic_folder=None):
        self.cancel_event = cancel_event
        self.emit = emit
        self.headless = headless
        self.url = url
        self.page = None
        self.browser = None
        self.manager = None
        self.playwright = None
        self.saving = False
        self.save_clicked = False
        self.diagnostic_folder = Path(diagnostic_folder) if diagnostic_folder else None
        self.dialog_timeout = 300
        self.last_portal_message = ""

    def check(self):
        if self.cancel_event.is_set():
            raise Cancelled("Cancelado pelo usuário.")

    async def open(self):
        self.check()
        if getattr(sys, "frozen", False):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(Path(sys._MEIPASS) / "browsers")
        self.manager = async_playwright()
        self.playwright = await self.manager.start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless, args=["--start-maximized"])
        context = await self.browser.new_context(viewport=None)
        self.page = await context.new_page()
        self.page.set_default_timeout(12000)
        async def dialog_handler(dialog):
            self.last_portal_message = dialog.message
            self.emit({"message": "Mensagem do SophiA: " + dialog.message})
            if self.saving:
                await dialog.accept()
            else:
                await dialog.dismiss()
        self.page.on("dialog", dialog_handler)
        await self.page.goto(self.url, wait_until="domcontentloaded")
        self.emit({"message": "Faça login na janela do navegador. Nenhuma senha será armazenada."})
        # Aguardar um menu autenticado, não qualquer redirecionamento.
        while True:
            self.check()
            if self.page.is_closed():
                raise RuntimeError("O navegador foi fechado antes do login.")
            if "lancnotas" in self.page.url.lower() or await self.page.get_by_text("Notas", exact=True).count():
                break
            await asyncio.sleep(0.3)
        await self.reset()

    async def close(self):
        try:
            if self.browser:
                await self.browser.close()
        finally:
            if self.manager and self.playwright:
                await self.playwright.stop()

    async def settle(self, cancellable=True):
        deadline = time.monotonic() + 20
        stable, last = 0, None
        while time.monotonic() < deadline:
            if cancellable:
                self.check()
            state = await self.page.evaluate("""() => {
                const manager = window.Sys?.WebForms?.PageRequestManager?.getInstance?.();
                if (manager?.get_isInAsyncPostBack() || document.readyState === 'loading') return null;
                return Array.from(document.querySelectorAll('select')).map(el => [el.id,el.value,el.disabled,Array.from(el.options).map(o=>o.value)]);
            }""")
            if state is not None and state == last:
                stable += 1
                if stable >= 3:
                    return
            else:
                stable = 0
            last = state
            await asyncio.sleep(0.25)
        raise RuntimeError("O portal não estabilizou os filtros após a operação.")

    async def reset(self, cancellable=True):
        if cancellable:
            self.check()
        await self.wait_for_portal_dialog()
        link = self.page.get_by_text("Notas", exact=True)
        if await link.count():
            await link.first.click()
        else:
            base = self.page.url.rsplit("/", 1)[0]
            await self.page.goto(base + "/LancNotas.aspx", wait_until="domcontentloaded")
        await self.settle(cancellable)

    async def _try_auto_confirm_success_dialog(self, text: str) -> bool:
        normalized = (text or "").lower()
        success_markers = (
            "as informações foram salvas com sucesso",
            "as informacoes foram salvas com sucesso",
            "dados salvos com sucesso",
            "gravado com sucesso",
        )
        if not any(marker in normalized for marker in success_markers):
            return False
        return await self.page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll("input[type='button'], input[type='submit'], button, a"));
            for (const btn of buttons) {
                const label = (btn.value || btn.innerText || '').trim().toLowerCase();
                if (label !== 'confirmar' && label !== 'ok') continue;
                const rect = btn.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && getComputedStyle(btn).visibility !== 'hidden') {
                    btn.click();
                    return true;
                }
            }
            return false;
        }""")

    async def wait_for_portal_dialog(self):
        overlay = self.page.locator(".cortinaDialogo:visible")
        if not await overlay.count():
            return
        dialog_script = """() => {
            const messages = Array.from(document.querySelectorAll('[role="dialog"], [class*="Dialogo"], .dialogo'))
                .filter(el => !el.matches('.cortinaDialogo') && el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden')
                .map(el => (el.innerText || '').trim()).filter(Boolean);
            return Array.from(new Set(messages)).join(' | ').slice(0, 1500);
        }"""
        text = await self.page.evaluate(dialog_script)
        self.last_portal_message = text or "Janela do SophiA aberta; texto não identificado automaticamente."
        self.emit({"message": "Janela do SophiA: " + self.last_portal_message})
        if await self._try_auto_confirm_success_dialog(self.last_portal_message):
            self.emit({"message": "Janela de confirmação de salvamento ('Confirmar') fechada automaticamente."})
            deadline_auto = time.monotonic() + 5.0
            while await overlay.count() and time.monotonic() < deadline_auto:
                await asyncio.sleep(0.1)
            await self.settle(cancellable=False)
            if not await overlay.count():
                return
        if self.diagnostic_folder:
            try:
                self.diagnostic_folder.mkdir(parents=True, exist_ok=True)
                path = self.diagnostic_folder / ("janela_sophia_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f") + ".png")
                await self.page.screenshot(path=str(path))
                self.emit({"message": "Imagem da janela do portal salva em: " + str(path)})
            except Exception as exc:
                self.emit({"message": "Não foi possível registrar a imagem da janela: " + str(exc)})
        self.emit({"message": "Aguardando a janela do SophiA: leia a mensagem e responda/feche a janela no navegador para continuar. Nenhum botão será clicado automaticamente nessa janela. Para interromper, use Cancelar no aplicativo."})
        deadline = time.monotonic() + self.dialog_timeout
        while await overlay.count():
            if self.cancel_event.is_set():
                raise Cancelled("Cancelado com janela do portal aberta; a gravação precisa ser conferida manualmente.")
            if time.monotonic() >= deadline:
                raise PortalDialogBlocked("A janela do SophiA permaneceu aberta. Resultado da gravação não confirmado. Mensagem: " + self.last_portal_message)
            latest_text = await self.page.evaluate(dialog_script)
            if latest_text and latest_text != self.last_portal_message:
                self.last_portal_message = latest_text
                self.emit({"message": "Nova mensagem na janela do SophiA: " + latest_text})
            await asyncio.sleep(0.2)
        await self.settle(cancellable=False)
        self.emit({"message": "Janela do portal fechada. Continuando a conferência dos valores; isso ainda não confirma a gravação."})

    async def selector(self, kind):
        result = await self.page.evaluate("""kind => {
            const matches = Array.from(document.querySelectorAll('select')).filter(el =>
                (el.id + ' ' + el.name).toLowerCase().includes(kind));
            if (matches.length !== 1) return null;
            const el = matches[0];
            return el.id ? '#' + CSS.escape(el.id) : 'select[name="' + CSS.escape(el.name) + '"]';
        }""", kind)
        if not result:
            raise RuntimeError(f"Não foi possível identificar o filtro '{kind}' no portal.")
        return result

    async def options(self, kind):
        selector = await self.selector(kind)
        rows = await self.page.locator(selector).evaluate("""el => Array.from(el.options).filter(o =>
            o.value && o.value !== '-1' && o.value !== '0' &&
            !/^(selecione|fim das etapas)/i.test(o.text.trim())
        ).map(o=>({value:o.value,text:o.text.trim()}))""")
        return [Option(**row) for row in rows]

    async def select(self, kind, option, cancellable=True):
        if cancellable:
            self.check()
        selector = await self.selector(kind)
        await self.page.locator(selector).select_option(option.value)
        await self.settle(cancellable)
        if await self.page.locator(await self.selector(kind)).input_value() != option.value:
            raise RuntimeError(f"O portal não manteve a seleção de {kind}: {option.text}.")

    async def restore(self, period, unit=None, classroom=None, stage=None, discipline=None, cancellable=True):
        # A ordem importa: cada postback pode limpar os filtros dependentes.
        await self.reset(cancellable)
        for kind, option in (("periodo", period), ("unidade", unit), ("turma", classroom), ("etapa", stage), ("disciplina", discipline)):
            if option:
                await self.select(kind, option, cancellable)

    async def button(self, names):
        for name in names:
            locator = self.page.get_by_role("button", name=name, exact=True)
            if await locator.count() == 1:
                return locator
            link = self.page.get_by_role("link", name=name, exact=True)
            if await link.count() == 1:
                return link
        raise RuntimeError("Botão não encontrado: " + "/".join(names))

    async def search(self, cancellable=True):
        if cancellable:
            self.check()
        await (await self.button(("Buscar", "Listar"))).click()
        await self.settle(cancellable)

    async def roster(self, exam):
        data = await self.page.evaluate(GRID_SCRIPT, exam)
        return data["header_found"], [Student(**row) for row in data["students"]]

    async def fill(self, student, value):
        self.check()
        if not student.input_selector:
            raise RuntimeError("Campo da avaliação ausente, bloqueado ou ambíguo.")
        locator = self.page.locator(student.input_selector)
        if await locator.count() != 1:
            raise RuntimeError("O campo da avaliação não é único.")
        await locator.fill(value)
        if await locator.input_value() != value:
            raise RuntimeError("O portal não aceitou o preenchimento da nota.")

    async def save_and_reload(self, task, exam):
        # Não interromper entre o clique e a releitura: registrar o resultado
        # dessa operação antes de atender ao cancelamento.
        self.check()
        self.save_clicked = False
        self.last_portal_message = ""
        self.saving = True
        try:
            button = await self.button(("Gravar", "Salvar"))
            self.save_clicked = True
            await button.click()
            await self.settle(cancellable=False)
            await self.wait_for_portal_dialog()
            await self.restore(task.period, task.unit, task.classroom, task.stage, task.discipline, cancellable=False)
            await self.search(cancellable=False)
            return (await self.roster(exam))[1]
        finally:
            self.saving = False
