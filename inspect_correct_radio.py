from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    info = page.evaluate("""() => {
        const inputs = Array.from(document.querySelectorAll('input[type="radio"], input[type="checkbox"], .iCheck-helper, [class*="radio"], [class*="check"]')).map(el => ({
            tagName: el.tagName,
            id: el.id,
            name: el.name,
            value: el.value,
            className: el.className,
            checked: el.checked,
            outerHTML: el.outerHTML.slice(0, 150)
        }));
        
        return inputs;
    }""")
    print("=== INPUTS / RADIOS ENCONTRADOS ===")
    for item in info:
        print(item)
