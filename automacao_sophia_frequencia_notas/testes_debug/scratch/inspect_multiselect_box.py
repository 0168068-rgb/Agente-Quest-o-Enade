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
        
    time.sleep(4)
    
    # Locate the first multiselect button under Filtros
    btn = page.locator("button.multiselect, button[title*='Educação'], button[title*='Semipresencial'], .filter-container button, div:has-text('Filtros:') ~ div button").first
    print("Found multiselect button:", btn.count())
    if btn.count() > 0:
        print(f"Button HTML: {btn.evaluate('el => el.outerHTML')}")
        print(f"Button Text: '{btn.inner_text().strip()}'")
        
        # Click the button to open menu
        print("Clicking multiselect button...")
        btn.click()
        time.sleep(2)
        
        # Check opened dropdown menu items
        items = page.locator("ul.multiselect-container li, .dropdown-menu li, div.dropdown-menu label")
        print(f"Dropdown menu items count: {items.count()}")
        for i in range(items.count()):
            it = items.nth(i)
            print(f" Item #{i}: text='{it.inner_text().strip()}', html='{it.evaluate('el => el.outerHTML')[:150]}'")
            
    context.close()
