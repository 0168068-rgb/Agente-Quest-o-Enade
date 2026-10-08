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
    
    # Wait for table DataTables to finish loading
    page.wait_for_selector("table tbody tr td", timeout=20000)
    time.sleep(3)
    
    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.is_visible():
            length_select.select_option("100")
            time.sleep(3)
    except Exception:
        pass

    rows = page.locator("table tbody tr")
    print(f"Total rows in main table: {rows.count()}")
    
    for i in range(rows.count()):
        tds = rows.nth(i).locator("td")
        if tds.count() > 3:
            disc = tds.nth(3).inner_text().strip()
            if "infraestrutura" in disc.lower():
                pre_val = tds.nth(12).inner_text().strip()
                print(f"DISCIPLINA: '{disc}' | PRÉ-VALIDADAS: '{pre_val}'")
                
                link = tds.nth(12).locator("a, button").first
                if link.count() > 0:
                    print("Opening pre-validated modal...")
                    link.click()
                    time.sleep(3)
                    
                    modal = page.locator("#myModal, .modal.show").first
                    q_rows = modal.locator("tbody tr")
                    print(f"Modal questions count: {q_rows.count()}")
                    if q_rows.count() > 0:
                        status_btn = q_rows.first.locator("button:has-text('Status'), .btn-success").first
                        status_btn.click()
                        time.sleep(2)
                        
                        desativar_btn = page.locator("[id*='btnDesativar'], a[href*='Desativar'], .fa-thumbs-down").first
                        print("Clicking desativar...")
                        desativar_btn.evaluate("el => el.click()")
                        time.sleep(3)
                        
                        print("\n==================================================")
                        print(" INSPECTION OF CANCELAR A QUESTÃO MODAL")
                        print("==================================================")
                        cancel_modal = page.locator(".modal:has-text('Cancelar'), [role='dialog']:has-text('Cancelar')").last
                        
                        # Outer HTML of cancel modal
                        full_html = cancel_modal.evaluate("el => el.outerHTML")
                        print("FULL OUTER HTML OF CANCEL MODAL:")
                        print(full_html)
                        print("==================================================\n")
                break
                
    time.sleep(5)
    context.close()
