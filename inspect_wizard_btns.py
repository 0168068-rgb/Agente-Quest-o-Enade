from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    btns = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button, a.btn, input[type="button"], input[type="submit"]'))
            .filter(b => b.offsetWidth > 0)
            .map(b => ({
                id: b.id,
                text: b.innerText.trim(),
                onclick: b.getAttribute('onclick') || '',
                class: b.className
            }));
    }""")
    print("=== BOTÕES VISÍVEIS NA PÁGINA ===")
    for b in btns:
        print(b)
