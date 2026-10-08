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
    
    print("\n1. Finding first dropdown button under Filtros...")
    filter_btn = page.locator("button.multiselect, .filter-container button, div:has-text('Filtros:') ~ div button, button[title*='Educação']").first
    print(f"   Button found: count={filter_btn.count()}, text='{filter_btn.inner_text().strip()}'")
    
    # Click the button physically
    filter_btn.click(force=True)
    time.sleep(1.5)
    page.screenshot(path="/home/hamilcar/Antigravity/scratch/multiselect_opened.png")
    print("   Screenshot saved to multiselect_opened.png")
    
    # Inspect all items in opened menu
    menu_items = page.locator("ul.multiselect-container li, .dropdown-menu li, .dropdown-menu label")
    print(f"   Menu items count: {menu_items.count()}")
    for i in range(menu_items.count()):
        item = menu_items.nth(i)
        print(f"      Item #{i}: text='{item.inner_text().strip()}'")
        
    # Uncheck Educação Semipresencial if checked, and check Ensino a distância
    for i in range(menu_items.count()):
        item = menu_items.nth(i)
        text = item.inner_text().strip().lower()
        chk = item.locator("input[type='checkbox']").first
        
        if "semipresencial" in text:
            if chk.count() > 0 and chk.is_checked():
                print("   Unchecking Educação Semipresencial...")
                chk.click(force=True)
                time.sleep(0.5)
        elif "distância" in text or "distancia" in text or "ead" in text:
            if chk.count() > 0 and not chk.is_checked():
                print(f"   Checking '{text}'...")
                chk.click(force=True)
                time.sleep(0.5)
            elif chk.count() == 0:
                print(f"   Clicking item '{text}' directly...")
                item.click(force=True)
                time.sleep(0.5)

    # Click body to close menu
    page.locator("body").click()
    time.sleep(3)
    page.screenshot(path="/home/hamilcar/Antigravity/scratch/multiselect_after_click.png")
    
    print(f"   Button text after update: '{filter_btn.inner_text().strip()}'")
    
    # Select 100 per page
    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.is_visible():
            length_select.select_option("100")
            time.sleep(3)
    except Exception as e:
        print("Select 100 error:", e)

    rows = page.locator("table tbody tr")
    print(f"\nTOTAL ROWS IN TABLE NOW: {rows.count()}")
    for r_idx in range(rows.count()):
        tds = rows.nth(r_idx).locator("td")
        if tds.count() > 3:
            disc_name = tds.nth(3).inner_text().strip()
            print(f" Row #{r_idx+1}: '{disc_name}'")
            if "infraestrutura" in disc_name.lower():
                print(f" *** FOUND TARGET DISCIPLINA ON ROW #{r_idx+1}: '{disc_name}' ***")

    time.sleep(5)
    context.close()
