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
    
    # Select Ensino a Distância
    selects = page.locator("select")
    for idx in range(selects.count()):
        s = selects.nth(idx)
        options = s.locator("option")
        for opt_idx in range(options.count()):
            opt_text = options.nth(opt_idx).inner_text().strip()
            if "distância" in opt_text.lower() or "distancia" in opt_text.lower():
                print(f"Selecting modality option #{opt_idx}: '{opt_text}'...")
                s.select_option(index=opt_idx)
                time.sleep(3)
                break

    # Select 100 per page
    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.is_visible():
            length_select.select_option("100")
            time.sleep(3)
    except Exception:
        pass

    rows = page.locator("table tbody tr")
    print(f"\nTOTAL DISCIPLINES IN 'Ensino a Distância': {rows.count()}")
    for i in range(rows.count()):
        tds = rows.nth(i).locator("td")
        if tds.count() > 3:
            disc_name = tds.nth(3).inner_text().strip()
            pre_val = tds.nth(12).inner_text().strip() if tds.count() > 12 else "N/A"
            print(f" Row #{i+1}: '{disc_name}' | Pré-validadas: {pre_val}")
            
    time.sleep(5)
    context.close()
