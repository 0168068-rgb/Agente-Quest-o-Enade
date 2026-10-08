from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = [pg for pg in context.pages if 'avalia' in pg.url][0]

    def handle_dialog(d):
        try:
            d.accept()
        except:
            pass
    page.on('dialog', handle_dialog)

    # 1. Select course in Step 2 if visible
    print("Selecting course in Step 2...")
    page.evaluate("""() => {
        const sel = document.getElementById('idCursoMatriz');
        if (sel) {
            // Select Redes de Computadores (46) or Gestão de TI (83) or ADS (45)
            const opt = Array.from(sel.options).find(o => o.text.includes('REDES') || o.text.includes('INFORMAÇÃO') || o.text.includes('ANÁLISE'));
            if (opt) sel.value = opt.value;
            else if (sel.options.length > 1) sel.value = sel.options[1].value;
            sel.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }""")
    time.sleep(1.5)

    # 2. Click Proximo (Step 2 -> Step 3)
    print("Clicking Proximo (Step 2 -> Step 3)...")
    page.evaluate("""() => {
        const btn = document.getElementById('buttonProximo');
        if (btn) btn.click();
    }""")
    time.sleep(2)

    # 3. Click Proximo (Step 3 -> Step 4)
    print("Clicking Proximo (Step 3 -> Step 4)...")
    page.evaluate("""() => {
        const btn = document.getElementById('buttonProximo');
        if (btn) btn.click();
    }""")
    time.sleep(2)

    print("Checking if #Questao_Nome is visible in Step 4:")
    v = page.evaluate("""() => {
        const q = document.getElementById('Questao_Nome');
        return q ? q.offsetWidth > 0 : false;
    }""")
    print("Questao_Nome visible:", v)
