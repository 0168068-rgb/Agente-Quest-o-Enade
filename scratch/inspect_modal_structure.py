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
    
    # Wait for table
    page.wait_for_selector("table tbody tr", timeout=20000)
    
    # Select 100
    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.is_visible():
            length_select.select_option("100")
            time.sleep(2)
    except Exception:
        pass
        
    # Find Infraestrutura row
    rows = page.locator("table tbody tr")
    for i in range(rows.count()):
        text = rows.nth(i).inner_text()
        if "infraestrutura" in text.lower():
            print(f"Found Infraestrutura row {i}")
            tds = rows.nth(i).locator("td")
            # find header index for pre-validada
            pre_val_link = tds.nth(12).locator("a, button").first
            if pre_val_link.count() > 0:
                print(f"Clicking pre-validated link (text: {pre_val_link.inner_text()})...")
                pre_val_link.click()
                time.sleep(3)
            break
            
    print("\n--- MODAL LIST OF QUESTIONS INSPECTION ---")
    page.wait_for_selector("#myModal, .modal.show", timeout=10000)
    main_modal = page.locator("#myModal, .modal.show").first
    print("Main Modal found!")
    
    m_rows = main_modal.locator("tbody tr")
    print(f"Total question rows in modal: {m_rows.count()}")
    if m_rows.count() > 0:
        first_row = m_rows.first
        print(f"First row text: {first_row.inner_text().strip()[:100]}")
        
        status_btn = first_row.locator("button, a").first
        print(f"Clicking status button (text: {status_btn.inner_text()})...")
        status_btn.click()
        time.sleep(2)
        
        desativar_btn = page.locator("[id*='btnDesativar'], a[href*='Desativar'], .fa-thumbs-down").first
        if desativar_btn.count() > 0:
            print(f"Desativar button HTML: {desativar_btn.evaluate('el => el.outerHTML')}")
            print("Clicking desativar button...")
            desativar_btn.evaluate("el => el.click()")
            time.sleep(3)
            
            modals = page.locator(".modal.show, .modal.in, [role='dialog']")
            print(f"\nOpen modals count: {modals.count()}")
            for mi in range(modals.count()):
                m = modals.nth(mi)
                if m.is_visible():
                    title = m.locator(".modal-title, h4, h5, header").inner_text() if m.locator(".modal-title, h4, h5, header").count() > 0 else "No Title"
                    print(f"\nModal #{mi} Title: '{title.strip()}'")
                    print(f"Modal #{mi} HTML snippet:\n{m.inner_html()[:600]}")
                    
                    forms = m.locator("form")
                    print(f"  Forms count: {forms.count()}")
                    for fi in range(forms.count()):
                        f = forms.nth(fi)
                        print(f"    Form {fi}: action='{f.get_attribute('action')}', method='{f.get_attribute('method')}', data-ajax='{f.get_attribute('data-ajax')}'")
                    
                    btns = m.locator("button, input[type='submit'], input[type='button'], a.btn")
                    for bi in range(btns.count()):
                        b = btns.nth(bi)
                        print(f"    Button {bi}: text='{b.inner_text().strip()}', type='{b.get_attribute('type')}', class='{b.get_attribute('class')}', onclick='{b.get_attribute('onclick')}'")

    print("\nSleeping 10s...")
    time.sleep(10)
    context.close()
