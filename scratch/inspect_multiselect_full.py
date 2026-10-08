import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"
TARGET_URL = "https://avalia.grupoa.com.br/Professor"

def get_logged_in_page(context):
    for p in reversed(context.pages):
        try:
            url = p.url
            if "Login" not in url and "avalia.grupoa.com.br" in url:
                return p
        except Exception:
            pass
    return None

def wait_for_login(context):
    print("\nVerificando login...")
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(2)
    
    check_count = 0
    while True:
        logged_page = get_logged_in_page(context)
        if logged_page:
            print(f"✓ Sessão autenticada: {logged_page.url}")
            return logged_page
        check_count += 1
        print(f"[{check_count}] Aguardando login...")
        time.sleep(3)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
    )
    page = wait_for_login(context)
    if TARGET_URL not in page.url:
        page.goto(TARGET_URL, wait_until="domcontentloaded")
        
    time.sleep(3)
    
    # Dump all buttons and selects under Filtros
    filter_info = page.evaluate("""() => {
        const selects = Array.from(document.querySelectorAll('select')).map(s => ({
            id: s.id,
            name: s.name,
            options: Array.from(s.options).map(o => ({ value: o.value, text: o.text, selected: o.selected }))
        }));
        
        const multiselects = Array.from(document.querySelectorAll('.btn-group, .dropdown')).map(g => {
            const btn = g.querySelector('button');
            const items = Array.from(g.querySelectorAll('li, label, a')).map(i => i.innerText.trim());
            return {
                btnText: btn ? btn.innerText.trim() : '',
                items: items
            };
        });
        
        return { selects, multiselects };
    }""")
    
    print("\n=== SELECTS ON PAGE ===")
    for s in filter_info['selects']:
        print(f"Select id='{s['id']}', name='{s['name']}':")
        for opt in s['options']:
            print(f"   Option value='{opt['value']}', text='{opt['text']}', selected={opt['selected']}")

    print("\n=== MULTISELECT GROUPS ON PAGE ===")
    for m in filter_info['multiselects']:
        print(f"Multiselect button text='{m['btnText']}':")
        for it in m['items'][:10]:
            print(f"   Item: '{it}'")
            
    # Click the first multiselect button and inspect container
    btn = page.locator("button.multiselect, button[title*='Educação'], button[title*='Semipresencial']").first
    if btn.count() > 0:
        btn.click()
        time.sleep(1)
        menu = page.locator("ul.multiselect-container, .dropdown-menu.show, div.dropdown-menu").first
        if menu.count() > 0:
            print("\nOPENED MENU HTML:")
            print(menu.evaluate("el => el.outerHTML"))
            
    time.sleep(5)
    context.close()
