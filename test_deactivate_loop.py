import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"
TARGET_URL = "https://avalia.grupoa.com.br/Professor"
TARGET_KEYWORDS = ["infraestrutura e serviços de ti", "infraestrutura e servicos de ti", "infraestrutura"]

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

def dismiss_toast_if_any(page):
    try:
        toasts = page.locator(".toast, .toast-error, .alert-danger, .toast-warning")
        if toasts.count() > 0:
            for i in range(toasts.count()):
                t = toasts.nth(i)
                if t.is_visible():
                    txt = t.inner_text().replace('\n', ' ')
                    print(f"   [Alerta do Sistema Fechado] {txt[:120]}...")
                    close_btn = t.locator(".toast-close-button, .close, [data-dismiss='alert']").first
                    if close_btn.count() > 0 and close_btn.is_visible():
                        close_btn.click(force=True)
    except Exception:
        pass

def close_cancel_modal_if_open(page):
    try:
        cancel_modals = page.locator(".modal.show:has-text('Cancelar'), .modal.in:has-text('Cancelar'), [role='dialog']:has-text('Cancelar')")
        if cancel_modals.count() > 0 and cancel_modals.last.is_visible():
            close_btn = cancel_modals.last.locator("button:has-text('Fechar'), .close, [data-dismiss='modal']").first
            if close_btn.count() > 0 and close_btn.is_visible():
                print("   [Ação] Fechando janela 'Cancelar a questão' pelo botão Fechar...")
                close_btn.click(force=True)
                page.wait_for_timeout(800)
    except Exception:
        pass

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
    
    # Select 100 per page
    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.is_visible():
            length_select.select_option("100")
            time.sleep(2)
    except Exception:
        pass

    # Find Infraestrutura row
    page.wait_for_selector("table tbody tr", timeout=15000)
    rows = page.locator("table tbody tr")
    
    target_row_idx = -1
    for i in range(rows.count()):
        text = rows.nth(i).inner_text()
        if any(kw in text.lower() for kw in TARGET_KEYWORDS):
            target_row_idx = i
            print(f"Disciplina encontrada na linha {i}: {text[:80]}...")
            break
            
    if target_row_idx == -1:
        print("Disciplina não encontrada!")
        context.close()
        exit(1)

    # Let's test 3 iterations with page refresh after each question
    for iteration in range(3):
        print(f"\n==================================================")
        print(f" TESTE ITERAÇÃO {iteration + 1}/3")
        print(f"==================================================")
        
        # 1. Reload page to ensure clean state and exact count
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(2)
        
        try:
            length_select = page.locator("select[name*='length'], select[name*='Table']").first
            if length_select.is_visible():
                length_select.select_option("100")
                time.sleep(2)
        except Exception:
            pass

        rows = page.locator("table tbody tr")
        target_row = rows.nth(target_row_idx)
        tds = target_row.locator("td")
        
        pre_val_td = tds.nth(12)
        count_text = pre_val_td.inner_text().strip()
        print(f"Contagem atual de Pré-Validadas: {count_text}")
        
        if not count_text.isdigit() or int(count_text) <= 10:
            print("Contagem <= 10 ou inválida. Parando teste.")
            break
            
        link = pre_val_td.locator("a, button").first
        print(f"Clicando no link de pré-validadas ({count_text})...")
        link.click()
        time.sleep(3)
        
        # 2. Main modal
        page.wait_for_selector("#myModal, .modal.show", timeout=10000)
        main_modal = page.locator("#myModal, .modal.show").first
        
        # Check first question row
        q_rows = main_modal.locator("tbody tr")
        if q_rows.count() == 0:
            print("Nenhuma questão na tabela do modal!")
            break
            
        first_q = q_rows.first
        print(f"Questão a ser desativada: {first_q.inner_text().strip()[:80]}...")
        
        # Click Status button on first question
        status_btn = first_q.locator("button:has-text('Status'), .btn-success, button").first
        print("PASSO 1: Clicando em Status...")
        status_btn.click()
        time.sleep(1.5)
        
        # Click btnDesativar
        desativar_btn = page.locator("[id*='btnDesativar'], a[href*='Desativar'], .fa-thumbs-down").first
        print("PASSO 2: Clicando em btnDesativar (polegar vermelho)...")
        desativar_btn.evaluate("el => el.click()")
        time.sleep(2)
        
        # Check cancel modal
        print("PASSO 3: Aguardando janela 'Cancelar a questão'...")
        cancel_modal = page.locator(".modal:has-text('Cancelar'), [role='dialog']:has-text('Cancelar')").last
        if cancel_modal.is_visible():
            print("Janela 'Cancelar a questão' visível!")
            
            # Check textarea
            desc_input = cancel_modal.locator("textarea[name*='Descricao'], textarea[id*='Descricao'], textarea").first
            if desc_input.count() > 0:
                print("PASSO 4: Preenchendo 'erro' na Descrição...")
                desc_input.fill("erro")
                time.sleep(1)
            
            # Check if there is a Salvar/Confirmar button inside cancel_modal
            salvar_btn = cancel_modal.locator("button:has-text('Salvar'), input[value*='Salvar'], button:has-text('Confirmar')").first
            if salvar_btn.count() > 0 and salvar_btn.is_visible():
                print("PASSO 5: Clicando em 'Salvar'...")
                salvar_btn.click()
                time.sleep(2)
            else:
                print("PASSO 5: Botão 'Salvar' não encontrado no modal. Fechando pelo 'Fechar'...")
                close_cancel_modal_if_open(page)
        else:
            print("Janela 'Cancelar a questão' não apareceu!")
            
        dismiss_toast_if_any(page)
        time.sleep(2)

    print("\nTeste concluído! Verificando resultado final...")
    page.goto(TARGET_URL, wait_until="networkidle")
    time.sleep(3)
    
    rows = page.locator("table tbody tr")
    target_row = rows.nth(target_row_idx)
    tds = target_row.locator("td")
    final_count = tds.nth(12).inner_text().strip()
    print(f"--> CONTAGEM FINAL DE PRÉ-VALIDADAS: {final_count}")
    
    context.close()
