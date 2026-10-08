from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    info = page.evaluate("""() => {
        const textareas = Array.from(document.querySelectorAll('textarea')).map(t => ({ id: t.id, name: t.name, class: t.className, visible: t.offsetWidth > 0 }));
        const iframes = Array.from(document.querySelectorAll('iframe')).map(i => ({ id: i.id, name: i.name, class: i.className, src: i.src }));
        const editables = Array.from(document.querySelectorAll('[contenteditable="true"]')).map(e => ({ id: e.id, class: e.className }));
        
        return {
            hasCKEDITOR: typeof CKEDITOR !== 'undefined',
            hasTinyMCE: typeof tinymce !== 'undefined',
            hasSummernote: typeof $.fn.summernote !== 'undefined',
            textareas,
            iframes,
            editables
        };
    }""")
    print("=== INFORMAÇÕES DE EDITORES NA PÁGINA ===")
    print(info)
