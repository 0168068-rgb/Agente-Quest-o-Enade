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
        print(f"[{check_count}] Aguardando login na tela do navegador...")
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
    
    # Inspect filters section
    filters = page.locator(".filter-container, #filtros, .row:has-text('Filtros'), div:has-text('Filtros:')")
    print("Filters section found:", filters.count())
    
    # Find all selects and dropdown buttons
    selects = page.locator("select")
    print("Select elements count:", selects.count())
    for s_idx in range(selects.count()):
        s = selects.nth(s_idx)
        print(f"Select #{s_idx}: id='{s.get_attribute('id')}', name='{s.get_attribute('name')}', class='{s.get_attribute('class')}'")
        options = s.locator("option")
        for o_idx in range(options.count()):
            o = options.nth(o_idx)
            print(f"   Option #{o_idx}: value='{o.get_attribute('value')}', text='{o.inner_text().strip()}'")

    # Find dropdown buttons (Bootstrap dropdown / Select2)
    btns = page.locator(".dropdown-toggle, button[data-toggle='dropdown'], div.btn-group button")
    print("\nDropdown buttons count:", btns.count())
    for b_idx in range(btns.count()):
        b = btns.nth(b_idx)
        print(f"Button #{b_idx}: text='{b.inner_text().strip()}', class='{b.get_attribute('class')}'")

    # Let's try clicking the first dropdown button or select
    ead_target = page.locator("select option:has-text('distância'), select option:has-text('Distância'), select option:has-text('EAD')")
    print("\nEAD options count:", ead_target.count())
    
    context.close()
