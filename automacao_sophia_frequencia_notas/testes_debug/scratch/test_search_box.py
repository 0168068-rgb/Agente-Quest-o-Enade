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
        
    time.sleep(4)
    
    # Locate DataTables search input
    search_inputs = page.locator("input[type='search'], .dataTables_filter input, input[placeholder*='busca'], input[placeholder*='Busca']")
    print(f"Search inputs count: {search_inputs.count()}")
    for i in range(search_inputs.count()):
        inp = search_inputs.nth(i)
        print(f" Search input #{i}: placeholder='{inp.get_attribute('placeholder')}', class='{inp.get_attribute('class')}'")
        
    if search_inputs.count() > 0:
        target_search = search_inputs.first
        print("Typing 'Infraestrutura' into search input...")
        target_search.fill("Infraestrutura")
        time.sleep(2)
        
        rows = page.locator("table tbody tr")
        print(f"\nFiltered rows count: {rows.count()}")
        for r_idx in range(rows.count()):
            row_text = rows.nth(r_idx).inner_text().replace('\n', ' ')
            print(f" Row #{r_idx+1}: {row_text[:120]}")
            
    time.sleep(5)
    context.close()
