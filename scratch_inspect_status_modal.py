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
        print("Aguardando login no navegador...")
        while "Login" in page.url:
            time.sleep(2)
            
    if page.url != TARGET_URL:
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(3)
    
    # Encontrar tabela de disciplinas com linhas
    tables = page.locator("table")
    best_table = None
    for i in range(tables.count()):
        t = tables.nth(i)
        if t.locator("tbody tr").count() > 0:
            best_table = t
            break
            
    if not best_table:
        print("Nenhuma tabela de disciplinas encontrada.")
        context.close()
        exit(0)
        
    row = best_table.locator("tbody tr").first
    td_pre_val = row.locator("td").nth(12)
    
    print("Clicando na célula de pré-validadas:", td_pre_val.inner_text())
    td_pre_val.locator("a").first.click()
    page.wait_for_timeout(3000)
    
    # Salvar snapshot da janela flutuante
    page.screenshot(path="/home/hamilcar/Antigravity/scratch_questions_modal.png")
    with open("/home/hamilcar/Antigravity/scratch_questions_modal.html", "w", encoding="utf-8") as f:
        f.write(page.content())
        
    print("Saved scratch_questions_modal.png / .html")
    context.close()
