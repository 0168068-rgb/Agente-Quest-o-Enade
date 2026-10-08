import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"
TARGET_URL = "https://avalia.grupoa.com.br/Professor"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False)
    page = context.pages[0] if context.pages else context.new_page()
    
    print("Navegando para a página do professor...")
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(3)
    
    if "Login" in page.url:
        print("Aguardando login...")
        while "Login" in page.url:
            time.sleep(2)
            
    if page.url != TARGET_URL:
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(3)

    # 1. Pegar 1ª tabela
    table = page.locator("table").nth(1)
    row = table.locator("tbody tr").first
    td_12 = row.locator("td").nth(12)
    print("Clicando na célula de pré-validadas:", td_12.inner_text())
    td_12.locator("a").first.click()
    page.wait_for_timeout(3000)
    
    # 2. Clicar no botão Status da 1ª questão
    main_modal = page.locator("#myModal, .modal.show").first
    status_btn = main_modal.locator("tr td button:has-text('Status'), tr td .btn-success").first
    status_btn.click(force=True)
    page.wait_for_timeout(1500)
    
    # 3. Clicar em btnDesativar (sem submeter nada ainda)
    desativar_btn = page.locator("[id*='btnDesativar'], a[href*='Desativar']").first
    print("Desativar btn href:", desativar_btn.get_attribute("href"))
    print("Desativar btn id:", desativar_btn.get_attribute("id"))
    
    # Abrir a janela "Cancelar a questão"
    page.evaluate("(el) => { el.style.display = 'inline-block'; el.click(); }", desativar_btn.element_handle())
    page.wait_for_timeout(2500)
    
    # 4. Dump do HTML da janela "Cancelar a questão"
    cancel_modal = page.locator(".modal:has-text('Cancelar'), [role='dialog']:has-text('Cancelar')").last
    cancel_html = cancel_modal.inner_html()
    
    with open("/home/hamilcar/Antigravity/scratch_cancel_modal.html", "w", encoding="utf-8") as f:
        f.write(cancel_html)
        
    print("\nHTML da janela Cancelar a questão salvo em scratch_cancel_modal.html!")
    
    soup = BeautifulSoup(cancel_html, "html.parser")
    forms = soup.find_all("form")
    print(f"\nFormulários encontrados ({len(forms)}):")
    for f in forms:
        print("Form attrs:", f.attrs)
        inputs = f.find_all(["input", "textarea", "button", "select"])
        for inp in inputs:
            print("  Input:", inp.name, inp.attrs)
            
    page.screenshot(path="/home/hamilcar/Antigravity/scratch_cancel_modal.png")
    context.close()
