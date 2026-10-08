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

    print("--- 1. Clicking AvaliA source button natively ---")
    btn = page.locator("button.btnFonteQuestao").filter(has_text="AvaliA").first
    if btn.count() > 0:
        btn.click()
        print("AvaliA clicked natively!")
    time.sleep(2)

    print("--- 2. Checking if buttonProximo or next step is active ---")
    page.evaluate("""() => {
        const btnNext = document.getElementById('buttonProximo') || document.querySelector('.buttonNext');
        if (btnNext) {
            btnNext.style.display = 'block';
            btnNext.click();
        }
    }""")
    time.sleep(2)

    print("Visible steps in modal:")
    steps = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('#myModal2 div[id*="step"]')).map(d => ({
            id: d.id, vis: d.offsetWidth > 0, text: d.innerText.slice(0, 100)
        })).filter(s => s.vis);
    }""")
    print(steps)
